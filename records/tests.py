from django.test import TestCase, TransactionTestCase
from django.core.management import call_command
from datetime import date
from records.search.record_search import birth_search, death_search, marriage_search
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

class SearchTests(TestCase):

    def setUp(self):

        # Location setup
        self.county = County.objects.create(county_code=1, county_name="Madison")
        self.city = City.objects.create(county=self.county, city_name="Edwardsville")

        # People
        self.john = Person.objects.create(
            first_name="John",
            last_name="Smith"
        )

        self.jane = Person.objects.create(
            first_name="Jane",
            last_name="Smythe"
        )

        self.bob = Person.objects.create(
            first_name="Robert",
            last_name="Johnson"
        )

        # Birth records
        self.birth1 = Birth.objects.create(
            person=self.john,
            birth_date=date(1900, 5, 1),
            birth_county=self.county,
            birth_city=self.city
        )

        self.birth2 = Birth.objects.create(
            person=self.jane,
            birth_date=date(1902, 6, 15),
            birth_county=self.county,
            birth_city=self.city
        )

        # Death record
        self.death1 = Death.objects.create(
            person=self.john,
            death_date=date(1980, 1, 1)
        )

        # Marriage record
        self.marriage = Marriage.objects.create(
            spouse1=self.john,
            spouse2=self.jane,
            marriage_date=date(1925, 7, 20),
            marriage_county=self.county,
            marriage_city=self.city
        )

    # ---------------------
    # Birth Search Tests
    # ---------------------

    def test_birth_exact_last_name(self):
        results = birth_search({"last_name": "Smith"})
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().person, self.john)

    def test_birth_percent_wildcard(self):
        results = birth_search({"last_name": "Sm%"})
        self.assertEqual(results.count(), 2)

    def test_birth_single_char_wildcard(self):
        results = birth_search({"last_name": "S_%th%"})
        self.assertEqual(results.count(), 2)

    def test_birth_date_variance(self):
        results = birth_search({
            "birth_date": "1900",
            "variance": "2"
        })
        self.assertEqual(results.count(), 2)

    def test_birth_city_filter(self):
        results = birth_search({"city_name": "Edward%"})
        self.assertEqual(results.count(), 2)

    # ---------------------
    # Death Search Tests
    # ---------------------

    def test_death_search_by_person(self):
        results = death_search({"last_name": "Smith"})
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().person, self.john)

    def test_death_date_variance(self):
        results = death_search({
            "death_date": "1980",
            "variance": "1"
        })
        self.assertEqual(results.count(), 1)

    # ---------------------
    # Marriage Search Tests
    # ---------------------

    def test_marriage_search_husband_name(self):
        results = marriage_search({"husband_last_name": "Smith"})
        self.assertEqual(results.count(), 1)

    def test_marriage_search_wife_name(self):
        results = marriage_search({"wife_last_name": "Smy%"})
        self.assertEqual(results.count(), 1)

    def test_marriage_date_variance(self):
        results = marriage_search({
            "marriage_date": "1925",
            "variance": "1"
        })
        self.assertEqual(results.count(), 1)

class FuzzySearchTest(TestCase):

    def setUp(self):
        # Create Counties
        self.county1 = County.objects.create(county_code=1, county_name="Madison")
        self.county2 = County.objects.create(county_code=2, county_name="Jefferson")

        # Create Cities
        self.city1 = City.objects.create(county=self.county1, city_name="Springfield")
        self.city2 = City.objects.create(county=self.county2, city_name="Franklin")

        # Create Persons
        self.person1 = Person.objects.create(first_name="John", middle_name="Lee", last_name="Smith", sex=Sex.MALE)
        self.person2 = Person.objects.create(first_name="Mary", middle_name="Ann", last_name="Miller", sex=Sex.FEMALE)
        self.person3 = Person.objects.create(first_name="Jon", middle_name="L", last_name="Smyth", sex=Sex.MALE)  # fuzzy test

        # Births
        self.birth1 = Birth.objects.create(person=self.person1, birth_date=date(1990, 5, 20),
                                           birth_county=self.county1, birth_city=self.city1)
        self.birth2 = Birth.objects.create(person=self.person3, birth_date=date(1991, 6, 15),
                                           birth_county=self.county2, birth_city=self.city2)

        # Deaths
        self.death1 = Death.objects.create(person=self.person2, death_date=date(2020, 1, 1),
                                           death_county=self.county1, death_city=self.city1, death_age=75)

        # Marriages
        self.marriage1 = Marriage.objects.create(spouse1=self.person1, spouse2=self.person2,
                                                 marriage_date=date(2015, 6, 1),
                                                 marriage_county=self.county1,
                                                 marriage_city=self.city1)

    def test_birth_fuzzy_search(self):
        # Pure fuzzy search by first/middle/last name
        filters = {"fuzzy_name": "Jon L Smyth"}
        results = birth_search(filters, fuzzy=True)
        self.assertIn(self.birth2, results)
        self.assertNotIn(self.birth1, results)  # person1 is John Lee Smith, shouldn't match this query

    def test_birth_filtered_plus_fuzzy(self):
        # Filter by county AND fuzzy name
        filters = {"fuzzy_name": "John Lee Smith", "birth_county": "Madison"}
        results = birth_search(filters, fuzzy=True)
        self.assertIn(self.birth1, results)
        self.assertNotIn(self.birth2, results)  # county doesn't match

    def test_death_fuzzy_search(self):
        filters = {"fuzzy_name": "Mary Ann Miller"}
        results = death_search(filters, fuzzy=True)
        self.assertIn(self.death1, results)

    def test_marriage_fuzzy_search(self):
        # Pure fuzzy for spouses
        filters = {"fuzzy_spouse1": "John Lee Smith", "fuzzy_spouse2": "Mary Ann Miller"}
        results = marriage_search(filters, fuzzy1=True, fuzzy2=True)
        self.assertIn(self.marriage1, results)

    def test_marriage_filtered_plus_fuzzy(self):
        # Filter by county and fuzzy spouse1
        filters = {"fuzzy_spouse1": "John Lee Smith", "spouse2_last_name": "Miller", "marriage_county": "Madison"}
        results = marriage_search(filters, fuzzy1=True, fuzzy2=False)
        self.assertIn(self.marriage1, results)