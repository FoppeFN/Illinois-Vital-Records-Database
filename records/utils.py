import csv
from pathlib import Path
from django.conf import settings

def load_county_choices():
    csv_path = "../data/counties.csv"
    #csv_path = settings.BASE_DIR / "data" / "counties.csv"

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [
            (row["county_code"], row["county"])
            for row in reader
        ]
    

def load_city_choices():
    csv_path = "../data/cities.csv"
    #csv_path = settings.BASE_DIR / "data" / "cities.csv"

    county_map = {}

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            county_code = row["county_code"]
            cities = [c.strip() for c in row["cities"].split(";")]
            county_map[county_code] = cities

    return county_map