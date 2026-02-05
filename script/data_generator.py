import json
import random
from datetime import date

RANDOM_SEED = 1337

CURRENT_YEAR = 1990  # cap

FIRST_NAMES_MALE = ["John", "William", "James", "Charles", "George", "Robert", "Edward"]
FIRST_NAMES_FEMALE = ["Mary", "Elizabeth", "Anna", "Margaret", "Helen", "Ruth", "Florence"]
LAST_NAMES = ["Smith", "Johnson", "Miller", "Brown", "Davis", "Wilson", "Anderson", "Taylor"]

COUNTIES = [
    "Madison",
    "St. Clair",
    "Cook",
    "Sangamon",
    "Champaign",
    "Peoria",
    "Kane",
    "Will",
]

BASE_START_YEAR = 1880
BASE_END_YEAR = 1950

LIFESPAN_MIN = 0                # allow infant deaths
LIFESPAN_MAX = 100

NUM_PEOPLE = 100                # how many people to generate     
MARRIAGE_PROB = 0.4             # 40% of people get a marriage record

MISSPELL_CHANCE = 0.05
BLANK_FIELD_CHANCE = 0.03


def init_random():
    random.seed(RANDOM_SEED)

def random_date_in_year(year: int) -> date:
    month = random.randint(1, 12)
    day = random.randint(1, 28)  # safe for all months
    return date(year, month, day)

def chance_misspell(name: str, chance: float = MISSPELL_CHANCE) -> str:
    if not name or len(name) < 3:
        return name
    if random.random() > chance:
        return name
    i = random.randint(0, len(name) - 2)
    chars = list(name)
    chars[i], chars[i + 1] = chars[i + 1], chars[i]
    return "".join(chars)

def chance_blank(value, chance: float = BLANK_FIELD_CHANCE):
    return "" if random.random() < chance else value

def norm(value: str) -> str:
    if value is None:
        return ""
    return "".join(value.lower().split())

def generate_person(person_id: int) -> dict:
    """
    Generate a 'person' object with birth & death info
    """

    is_male = random.random() < 0.5     # "random boolean"
    gender = "M" if is_male else "F"
    first_name = random.choice(FIRST_NAMES_MALE if is_male else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    county_of_birth = random.choice(COUNTIES)

    birth_year = random.randint(BASE_START_YEAR, BASE_END_YEAR)
    birth_date = random_date_in_year(birth_year)

    lifespan = random.randint(LIFESPAN_MIN, LIFESPAN_MAX)
    death_year = birth_year + lifespan

    
    if death_year > CURRENT_YEAR:       # ensure not in the future
    # died sometime in the last 1–5 years before CURRENT_YEAR
        death_year = CURRENT_YEAR - random.randint(1, 5)

    if death_year < birth_year:
        death_year = birth_year         # edge case

    death_date = random_date_in_year(death_year)

    person = {
        "person_id": person_id,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender,
        "birth_date": birth_date,
        "death_date": death_date,
        "county_of_birth": county_of_birth,
        "status": "Unmarried",                  # add marriages later
    }
    return person

def make_birth_record_from_person(person: dict) -> dict:
    first = chance_misspell(person["first_name"])
    last = chance_misspell(person["last_name"])
    # simple fake parents (not stored as separate persons)
    mother_first = chance_blank(chance_misspell(random.choice(FIRST_NAMES_FEMALE)))
    father_first = chance_blank(chance_misspell(random.choice(FIRST_NAMES_MALE)))

    return {
        "record_id": f"B{person['person_id']:05d}",
        "record_type": "birth",
        "person_id": person["person_id"],
        "first_name": first,
        "last_name": last,
        "sex": person["gender"],
        "date_of_birth": person["birth_date"].isoformat(),
        "county": person["county_of_birth"],
        "mother_first_name": mother_first,
        "mother_last_name": chance_blank(last),
        "father_first_name": father_first,
        "father_last_name": chance_blank(last),
        "first_name_norm": norm(first),
        "last_name_norm": norm(last),
    }


def make_death_record_from_person(person: dict) -> dict:
    first = chance_misspell(person["first_name"])
    last = chance_misspell(person["last_name"])

    return {
        "record_id": f"D{person['person_id']:05d}",
        "record_type": "death",
        "person_id": person["person_id"],
        "first_name": first,
        "last_name": last,
        "date_of_birth": person["birth_date"].isoformat(),
        "date_of_death": person["death_date"].isoformat(),
        "county": person["county_of_birth"],
        "first_name_norm": norm(first),
        "last_name_norm": norm(last),
    }


def make_marriage_record(person1: dict, person2: dict, marriage_id: int) -> dict:
    """
    Pair two people and marry them, assuming they keep / share last name.
    """
    # choose a marriage year between both birth years + 16 and CURRENT_YEAR
    min_year = max(person1["birth_date"].year + 16,
                   person2["birth_date"].year + 16,
                   BASE_START_YEAR)
    max_year = min(CURRENT_YEAR, min_year + 50)
    m_year = random.randint(min_year, max_year)
    m_date = random_date_in_year(m_year)

    # assume spouse2 takes spouse1's last name
    last_name = person1["last_name"]

    s1_first = chance_misspell(person1["first_name"])
    s2_first = chance_misspell(person2["first_name"])
    last_name = chance_misspell(last_name)

    return {
        "record_id": f"M{marriage_id:05d}",
        "record_type": "marriage",
        "spouse1_person_id": person1["person_id"],
        "spouse2_person_id": person2["person_id"],
        "spouse1_first_name": s1_first,
        "spouse1_last_name": last_name,
        "spouse2_first_name": s2_first,
        "spouse2_last_name": last_name,
        "date_of_marriage": m_date.isoformat(),
        "county": random.choice(COUNTIES),
        "first_name_norm": norm(s1_first),
        "last_name_norm": norm(last_name),
    }

def generate_all_records():
    init_random()

    people = [generate_person(i) for i in range(1, NUM_PEOPLE + 1)]

    records = []

    # Everyone gets a birth & death record
    for p in people:
        records.append(make_birth_record_from_person(p))
        records.append(make_death_record_from_person(p))

    # Randomly pick pairs for marriages
    candidates = people.copy()
    random.shuffle(candidates)
    marriage_id = 1
    for i in range(0, len(candidates) - 1, 2):
        if random.random() > MARRIAGE_PROB:
            continue
        p1 = candidates[i]
        p2 = candidates[i + 1]
        records.append(make_marriage_record(p1, p2, marriage_id))
        marriage_id += 1

    return records

def main():
    records = generate_all_records()
    out_path = "mock_records.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
