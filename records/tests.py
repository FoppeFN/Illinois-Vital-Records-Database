import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError
from .models import Person, Birth, Death, Marriage, Sex
from datetime import date

class PersonModelTest(TestCase):

    def setUp(self):
        # Create some persons
        self.jane = Person.objects.create(
            first_name="Jane",
            last_name="Doe",
            sex=Sex.FEMALE
        )
        self.john = Person.objects.create(
            first_name="John",
            last_name="Smith",
            sex=Sex.MALE
        )
        self.child = Person.objects.create(
            first_name="Baby",
            last_name="Doe",
            sex=Sex.FEMALE,
            mother=self.jane,
            father=self.john
        )

    def test_children_relationship(self):
        # Jane should have one child
        jane_children = list(self.jane.children)
        self.assertIn(self.child, jane_children)
        self.assertEqual(len(jane_children), 1)

        # John should also have one child
        john_children = list(self.john.children)
        self.assertIn(self.child, john_children)
        self.assertEqual(len(john_children), 1)

    def test_birth_death_records(self):
        # Test Birth record creation
        birth_image = SimpleUploadedFile("birth.jpg", b"file_content", content_type="image/jpeg")
        birth = Birth.objects.create(
            birth_date=date(2000, 1, 1),
            birth_county="001",
            birth_record_image=birth_image
        )
        self.assertEqual(birth.birth_county, "001")
        # Check that the file name starts with "birth" (ignore random suffix)
        self.assertTrue(os.path.basename(birth.birth_record_image.name).startswith("birth"))

        # Test Death record creation
        death_image = SimpleUploadedFile("death.jpg", b"file_content", content_type="image/jpeg")
        death = Death.objects.create(
            death_date=date(2050, 12, 31),
            death_county="002",
            death_record_image=death_image
        )
        self.assertEqual(death.death_county, "002")
        self.assertTrue(os.path.basename(death.death_record_image.name).startswith("death"))

    def test_marriage_creation_and_ordering(self):
        # Marriage image
        marriage_image = SimpleUploadedFile("marriage.jpg", b"file_content", content_type="image/jpeg")

        # Create marriage with spouse2 ID < spouse1 ID to test automatic ordering
        if self.john.id < self.jane.id:
            spouse1, spouse2 = self.john, self.jane
        else:
            spouse1, spouse2 = self.jane, self.john

        marriage = Marriage.objects.create(
            spouse1=spouse2,  # intentionally reversed
            spouse2=spouse1,
            marriage_date=date(2025, 6, 15),
            marriage_county="003",
            death_record_image=marriage_image
        )

        # After save, spouse1 should have lower ID
        self.assertLess(marriage.spouse1.id, marriage.spouse2.id)

        # Check that the marriage image file name starts with "marriage"
        self.assertTrue(os.path.basename(marriage.death_record_image.name).startswith("marriage"))

        # Check uniqueness constraint: trying to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            Marriage.objects.create(
                spouse1=marriage.spouse1,
                spouse2=marriage.spouse2,
                marriage_date=date(2025, 6, 15)
            )