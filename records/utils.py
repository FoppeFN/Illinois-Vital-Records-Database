import csv
from django.conf import settings

def load_county_choices():
    csv_path = settings.BASE_DIR / "data" / "counties.csv"

    with open(csv_path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [
            (row["county_code"], row["county"])
            for row in reader
        ]