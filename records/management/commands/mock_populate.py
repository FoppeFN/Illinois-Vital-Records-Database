from django.core.management.base import BaseCommand

from records.image_utils import (
    generate_birth_certificate_image,
    generate_death_certificate_image,
    image_to_content_file,
)
from records.models import Birth, City, County, Death, Marriage, Person, Sex
from records.utils import load_mock_data


class Command(BaseCommand):
    help = "Load mock genealogy data into the database"

    def handle(self, *args, **kwargs):
        _, people, marriages = load_mock_data()

        person_map = {}
        image_count = 0

        for pid, pdata in people.items():
            if pdata["sex"] == "M":
                sex = Sex.MALE
            elif pdata["sex"] == "F":
                sex = Sex.FEMALE
            else:
                sex = Sex.UNKNOWN

            person = Person.objects.create(
                first_name=pdata["first"],
                middle_name=pdata["middle"],
                last_name=pdata["last"],
                sex=sex,
            )

            b_county = County.objects.get(county_code=pdata["birth_county_code"])
            b_city = City.objects.get(county=b_county, city_name=pdata["birth_city"])

            d_county = County.objects.get(county_code=pdata["death_county_code"])
            d_city = City.objects.get(county=d_county, city_name=pdata["death_city"])

            birth_obj = Birth.objects.create(
                person=person,
                birth_date=pdata["birth_date"],
                birth_county=b_county,
                birth_city=b_city,
            )

            death_obj = Death.objects.create(
                person=person,
                death_date=pdata["death_date"],
                death_age=pdata["age"],
                death_county=d_county,
                death_city=d_city,
            )

            person_map[pid] = person

        for pid, pdata in people.items():
            person = person_map[pid]

            if pdata.get("mother"):
                person.mother = person_map[pdata["mother"]]

            if pdata.get("father"):
                person.father = person_map[pdata["father"]]

            person.save()

            if image_count < 100:
                birth_obj = person.birth.first()
                death_obj = person.death.first()

                birth_img = generate_birth_certificate_image(person, birth_obj)
                birth_obj.birth_record_image.save(
                    f"birth_{person.id}.png",
                    image_to_content_file(birth_img, f"birth_{person.id}.png"),
                    save=True,
                )

                death_img = generate_death_certificate_image(person, death_obj)
                death_obj.death_record_image.save(
                    f"death_{person.id}.png",
                    image_to_content_file(death_img, f"death_{person.id}.png"),
                    save=True,
                )

                image_count += 1

        for marriage in marriages:
            m_county = County.objects.get(county_code=marriage["marriage_county"][0])
            m_city = City.objects.get(
                county=m_county, city_name=marriage["marriage_city"]
            )

            Marriage.objects.create(
                spouse1=person_map[marriage["spouse1"]],
                spouse2=person_map[marriage["spouse2"]],
                marriage_date=marriage["marriage_date"],
                marriage_county=m_county,
                marriage_city=m_city,
            )

        self.stdout.write(
            self.style.SUCCESS("Database populated with mock data successfully")
        )
