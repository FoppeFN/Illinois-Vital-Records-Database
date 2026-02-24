from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from records.models import Person, Birth, Death, Marriage, Sex, County, City

class GenealogyDataTest(TestCase):

    def test_parent_child_relationships(self):
        for person in Person.objects.all():
            # If person has a mother/father, ensure child appears in their children
            if person.mother:
                self.assertIn(person, person.mother.children())
            if person.father:
                self.assertIn(person, person.father.children())

    def test_siblings(self):
        for person in Person.objects.all():
            siblings = person.siblings()
            # Person should not appear in their own siblings list
            self.assertNotIn(person, siblings)
            # Siblings must share at least one parent
            for sib in siblings:
                self.assertTrue(
                    person.mother == sib.mother or person.father == sib.father
                )

    def test_birth_death_linkage(self):
        for person in Person.objects.all():
            # Ensure person has at most one birth/death record
            self.assertLessEqual(person.birth.count(), 1)
            self.assertLessEqual(person.death.count(), 1)
            if person.birth.exists():
                birth = person.birth.first()
                self.assertEqual(birth.person, person)
            if person.death.exists():
                death = person.death.first()
                self.assertEqual(death.person, person)

    def test_marriages(self):
        for marriage in Marriage.objects.all():
            # Spouses must be Persons
            self.assertIsInstance(marriage.spouse1, Person)
            self.assertIsInstance(marriage.spouse2, Person)
            # Marriage date should exist
            self.assertIsNotNone(marriage.marriage_date)
            # Marriage should appear in spouses' reverse relations
            self.assertIn(marriage, marriage.spouse1.marriages_as_spouse1.all() | marriage.spouse1.marriages_as_spouse2.all())
            self.assertIn(marriage, marriage.spouse2.marriages_as_spouse1.all() | marriage.spouse2.marriages_as_spouse2.all())

class MockDataIntegrityTest(TestCase):
    """
    Verify the integrity of the mock genealogy dataset.
    """

    def test_counties_have_unique_codes(self):
        codes = County.objects.values_list('county_code', flat=True)
        self.assertEqual(len(codes), len(set(codes)), "Duplicate county codes found!")

    def test_cities_have_county(self):
        for city in City.objects.all():
            self.assertIsNotNone(city.county, f"City '{city.city_name}' has no county set!")

    def test_person_has_valid_sex(self):
        for person in Person.objects.all():
            self.assertIn(person.sex, [Sex.MALE, Sex.FEMALE, Sex.UNKNOWN], 
                        f"Person '{person}' has invalid sex '{person.sex}'")

    def test_births_and_deaths_link_to_person_and_county(self):
        for birth in Birth.objects.all():
            self.assertIsNotNone(birth.person, "Birth without a person")
            self.assertIsNotNone(birth.birth_county, f"Birth for {birth.person} has no county")
            self.assertIsNotNone(birth.birth_city, f"Birth for {birth.person} has no city")
        
        for death in Death.objects.all():
            self.assertIsNotNone(death.person, "Death without a person")
            self.assertIsNotNone(death.death_county, f"Death for {death.person} has no county")
            self.assertIsNotNone(death.death_city, f"Death for {death.person} has no city")

    def test_parent_child_consistency(self):
        for person in Person.objects.all():
            if person.mother:
                self.assertIn(person, person.mother.children(), 
                            f"{person} not listed as child of mother {person.mother}")
            if person.father:
                self.assertIn(person, person.father.children(), 
                            f"{person} not listed as child of father {person.father}")

    def test_sibling_consistency(self):
        for person in Person.objects.all():
            for sibling in person.siblings():
                # Sibling should share at least one parent
                shared_parent = (person.mother and person.mother == sibling.mother) or \
                                (person.father and person.father == sibling.father)
                self.assertTrue(shared_parent, 
                                f"{person} and {sibling} reported as siblings but share no parent")

    def test_marriages_validity(self):
        for marriage in Marriage.objects.all():
            self.assertNotEqual(marriage.spouse1, marriage.spouse2,
                                f"Marriage has same person as both spouses: {marriage.spouse1}")
            self.assertIsNotNone(marriage.marriage_county,
                                f"Marriage between {marriage.spouse1} & {marriage.spouse2} has no county")
            self.assertIsNotNone(marriage.marriage_city,
                                f"Marriage between {marriage.spouse1} & {marriage.spouse2} has no city")

    def test_sex_specific_children_methods(self):
        for person in Person.objects.all():
            sons = person.sons()
            daughters = person.daughters()
            self.assertTrue(all(child.sex == Sex.MALE for child in sons),
                            f"{person} has a son with wrong sex")
            self.assertTrue(all(child.sex == Sex.FEMALE for child in daughters),
                            f"{person} has a daughter with wrong sex")
            

class FamilyStructureTestPopulatedDB(TestCase):
    """
    Tests that after initializing and populating the database:
    1. There exists a family line (ancestor chain) of depth >= 6
    2. There exists at least one set of siblings of breadth >= 3
    """

    @classmethod
    def setUpTestData(cls):
        # Initialize the database tables
        call_command('init_db', verbosity=0)
        # Populate the database with mock data
        call_command('mock_populate', verbosity=0)

    def test_family_line_depth(self):
        """
        Check that some person has a lineage (following mothers or fathers) of at least 6 generations.
        """
        def get_lineage_depth(person, lineage_attr='mother', depth=0):
            parent = getattr(person, lineage_attr)
            if not parent:
                return depth
            return get_lineage_depth(parent, lineage_attr, depth + 1)

        max_depth = 0
        for person in Person.objects.all():
            depth_mother = get_lineage_depth(person, 'mother')
            depth_father = get_lineage_depth(person, 'father')
            max_depth = max(max_depth, depth_mother, depth_father)

        self.assertGreaterEqual(
            max_depth,
            6,
            f"No family line with depth >= 6 found (max depth: {max_depth})"
        )

    def test_sibling_breadth(self):
        """
        Check that some person has at least 2 siblings (breadth >= 3 including self)
        """
        max_siblings = 0
        for person in Person.objects.all():
            siblings_count = person.siblings().count() + 1  # +1 to include self
            max_siblings = max(max_siblings, siblings_count)

        self.assertGreaterEqual(
            max_siblings,
            3,
            f"No sibling set with breadth >= 3 found (max breadth: {max_siblings})"
        )

class ParentPresenceTest(TestCase):
    """
    Tests that every person in the database has at least one parent assigned.
    """

    def test_people_have_parents(self):
        people_without_parents = Person.objects.filter(mother__isnull=True, father__isnull=True)
        count = people_without_parents.count()

        self.assertEqual(
            count, 
            0,
            f"{count} person(s) have no mother or father assigned: {[p.id for p in people_without_parents]}"
        )