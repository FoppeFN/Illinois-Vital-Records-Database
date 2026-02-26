from records.models import County, City
from records.utils import load_county_choices, load_city_choices
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Initialize database with 2026 counties and some cities"

    def handle(self, *args, **kwargs):
        counties = load_county_choices()
        cities = load_city_choices()

        for county in counties:
            c_obj, _ = County.objects.get_or_create(
                county_code=int(county[0]),
                county_name=county[1]
            )

            for city in cities[county[0]]:
                City.objects.get_or_create(
                    county=c_obj,
                    city_name=city
                )
        
        self.stdout.write(self.style.SUCCESS("Database initialized successfully"))