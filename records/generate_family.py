from faker import Faker
import numpy as np
import random
import json
import csv
import os
from utils import load_county_choices, load_city_choices
from pathlib import Path
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from argparse import ArgumentParser

fake = Faker()

# -----------------------------
# CONFIG
# -----------------------------
PCP = 0.69                 # Partnered-with-children probability
CD_MEAN, CD_SD = 2.0, 1.5  # Child distribution (Normal)
MAX_CHILDREN = 10




FTDL = 6                   # Family Tree Depth Limit
SPDL = 3                   # Sibling-Partner Depth Limit


# -----------------------------
# GLOBAL STATE
# -----------------------------
people = {}        # person_id -> dict
_id = 0
counties = []      # list of {"county_code": "...", "county": "..."}
city = {}
marriages = {}
_mid = 0


# Age States
min_age = 18
max_age = 115
mean_age = 68
sd_age = 15

birth_date_seed = date(1920, 6, 15)

young_offset = 18
old_offset = -18

"""
fake.date_between(
    start_date=date(1900, 1, 1),
    end_date=date(1950, 12, 31)
)
"""

"""
1. Birth date
2. Age
3. Death date = birth date + age in range as in 1980-06-15 -- 1981-06-14
"""



# -----------------------------
# HELPERS
# -----------------------------
def new_id():
    global _id
    _id += 1
    return f"P{_id:06d}"


def pick_death_date(birth_date, age):
    start = birth_date + relativedelta(years=age)
    end = birth_date + relativedelta(years = age + 1) - timedelta(days = 1)
    return fake.date_between(start_date=start, end_date=end)


def pick_age():
    return int(np.random.normal(mean_age, sd_age))


def pick_birth_date(seed, age_offset):
    start = seed + relativedelta(years=(age_offset - 2))
    end = seed + relativedelta(years=(age_offset + 2))
    return fake.date_between(start_date=start, end_date=end)


def pick_marriage_date(seed):
    start = seed + relativedelta(years=16)
    end = seed + relativedelta(years=22)
    return fake.date_between(start_date=start, end_date=end)


def pick_county():
    """
    Random county selection (uniform).
    """
    return random.choice(counties)


def pick_city(county):
    """
    Random city selection (uniform).
    """
    return random.choice(cities[county[0]])


def child_count(require_at_least_one: bool):
    """
    Samples from N(mean, sd), rounds, clamps to [0..MAX_CHILDREN].
    """
    n = int(round(np.random.normal(CD_MEAN, CD_SD)))
    n = max(0, min(MAX_CHILDREN, n))
    if require_at_least_one:
        n = max(1, n)
    return n


def marry(p1, p2):
    """
    Adds spouse IDs to each person's marriages list (no duplicates).
    """
    spouse_list = sorted([p1, p2])

    marriage_id = spouse_list[0] + "," + spouse_list[1]
    marriage_county = pick_county()
    marriage_city = pick_city(marriage_county)
    marriage_date = pick_marriage_date(people[p1]["birth_date"]).isoformat()

    if people[p1]["sex"] == "F": people[p1]["last"] = people[p2]["last"]
    if people[p2]["sex"] == "F": people[p2]["last"] = people[p1]["last"]

    if marriage_id not in marriages:
        marriages[marriage_id] = {
            "spouse1": p1,
            "spouse2": p2,
            "marriage_county": marriage_county,
            "marriage_city": marriage_city,
            "marriage_date": marriage_date
        }
        people[p1]["is_married"] = True
        people[p2]["is_married"] = True
    

# -----------------------------
# PERSON + FAMILY CREATION
# -----------------------------
def make_person(sex=None, last=None, birth_seed=birth_date_seed, age_offset=0):
    """
    Creates a person with:
    - id, first, last, sex
    - birth_county + birth_county_code (from CSV)
    - parent links (mother/father)
    - children list
    - marriages list

    sex: "M", "F", "U" or None (random)
    last: optional last name override
    """
    # sex selection (small % unknown)
    if sex is None:
        r = random.random()
        sex = "M" if r < 0.49 else ("F" if r < 0.98 else "U")

    if sex == "M":
        first = fake.first_name_male()
        middle = fake.first_name_male()
    elif sex == "F":
        first = fake.first_name_female()
        middle = fake.first_name_female()
    else:
        first = fake.first_name()
        middle = fake.first_name()

    pid = new_id()
    last = last or fake.last_name()

    birth_county = pick_county()
    death_county = pick_county()

    birth_city = pick_city(birth_county)
    death_city = pick_city(death_county)

    birth_date = pick_birth_date(birth_seed, age_offset)
    age = pick_age()
    death_date = pick_death_date(birth_date, age)

    people[pid] = {
        "id": pid,
        "first": first,
        "middle": middle,
        "last": last,
        "sex": sex,

        # birth county info from CSV
        
        "birth_county_code": birth_county[0],
        "birth_county": birth_county[1],
        "birth_city": birth_city,

         
        "death_county_code": death_county[0],
        "death_county": death_county[1],
        "death_city": death_city,


        # dates

        "birth_date": birth_date,
        "death_date": death_date,
        "age": age,

        #marriage
        "is_married": False,

        # parents
        "mother": None,
        "father": None,

        # children
        "children": [],
    }

    return pid


def make_children(mom, dad, require_at_least_one=False):
    """
    Generates a child cluster (CC) for mom+dad.
    Children default to dad's last name.
    Returns list of child IDs.
    """
    n = child_count(require_at_least_one)
    kids = []

    base_last = people[dad]["last"]  # early-1900s default

    for _ in range(n):
        birth_seed = people[mom]["birth_date"]
        k = make_person(last=base_last, birth_seed=birth_seed, age_offset=young_offset)

        # link parents
        people[k]["mother"] = mom
        people[k]["father"] = dad

        # link children arrays
        people[mom]["children"].append(k)
        people[dad]["children"].append(k)

        kids.append(k)

    return kids


def make_sibling_cluster(person):
    person_info = people[person]

    sibling_count = child_count(require_at_least_one=True) - 1
    sibling_cluster = [person]

    for _ in range(sibling_count):
        sibling_cluster.append(make_person(last=person_info["last"], birth_seed=person_info["birth_date"]))
    
    return sibling_cluster


def expand_from_cluster(cluster, depth, sp_depth):
    """
    Expands relationships starting from a CC (cluster of siblings).
    Stops at FTDL and SPDL.
    """

    if depth >= FTDL:
        return
    
    if len(cluster) < 1:
        return

    # Create parents for this CC(i)
    # PARENTS (OLDER AGE)
    rand_child = cluster[0]
    birth_seed = people[rand_child]["birth_date"]

    mom = make_person(sex="F", birth_seed=birth_seed, age_offset=old_offset)
    dad = make_person(sex="M", birth_seed=birth_seed, age_offset=old_offset)
    marry(mom, dad)

    # Attach these parents to every child in the cluster
    for child in cluster:
        people[child]["mother"] = mom
        people[child]["father"] = dad
        people[mom]["children"].append(child)
        people[dad]["children"].append(child)

    mom_cluster = make_sibling_cluster(mom)
    dad_cluster = make_sibling_cluster(dad)

    # For each sibling in CC(i), maybe partner + children
    for person in cluster:
        if people[person]["is_married"]:
            continue
        if people[person]["sex"] == "U":
            continue  # unknown sex rule: no PC / no children
        if random.random() > PCP:
            continue

        # PARTNER (SAME AGE)
        partner_sex = "F" if people[person]["sex"] == "M" else "M"
        partner = make_person(sex=partner_sex, birth_seed=birth_seed)
        marry(person, partner)

        # kids for this couple
        # CHILDREN (YOUNGER AGE)
        m = person if people[person]["sex"] == "F" else partner
        d = person if people[person]["sex"] == "M" else partner
        make_children(m, d)

        # Expand partner siblings (SPDL)
        # SIBLINGS (SAME AGE)
        if sp_depth + 1 < SPDL:
            # make a tiny "partner sibling cluster" (partner + one sibling)
            sibling_cluster = make_sibling_cluster(partner)
            expand_from_cluster(sibling_cluster, depth, sp_depth + 1)

    expand_from_cluster(mom_cluster, depth + 1, sp_depth)
    expand_from_cluster(dad_cluster, depth + 1, sp_depth)


def generate():
    """
    Step 1: initial CC(i)-f
    """
    # fake parents not used in family tree. just for seeding ===
    mom = make_person(sex="F", birth_seed=birth_date_seed)
    dad = make_person(sex="M", birth_seed=birth_date_seed)
    marry(mom, dad)
    # ==========================================================

    # begin generation
    root_cc = make_children(mom, dad, require_at_least_one=True)

    expand_from_cluster(root_cc, depth=0, sp_depth=0)
    return root_cc


def save_json(filepath: str, obj: dict):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # Seeds for repeatable output
    np.random.seed(7)
    random.seed(7)
    Faker.seed(7)

    # Load counties
    # Put your CSV at: data/counties.csv
    counties = load_county_choices()
    cities = load_city_choices()

    # Generate
    root_cluster = generate()

    # Wrap output with metadata

    for person_id, info in people.items():
        info["birth_date"] = info["birth_date"].isoformat()
        info["death_date"] = info["death_date"].isoformat()


    output = {
        "meta": {
            "pcp": PCP,
            "cd_mean": CD_MEAN,
            "cd_sd": CD_SD,
            "ftdl": FTDL,
            "spdl": SPDL,
            "root_cluster_child_ids": root_cluster,
            "total_people": len(people),
        },
        "people": people,
        "marriages": marriages
    }

    # Save JSON
    out_path = "../output/family_tree.json"
    save_json(out_path, output)

    print("Wrote:", out_path)
    print("Total people:", len(people))