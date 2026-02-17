from faker import Faker
import random
import json
from datetime import date
from pathlib import Path

fake = Faker()
NUM_RECORDS = 50

FILE = Path("death_records.json")

ILLINOIS_COUNTIES =[
    "Adams", "Alexander", "Bond", "Boone", "Brown", "Bureau",
    "Calhoun", "Carroll", "Cass", "Champaign", "Christian", "Clark",
    "Clay", "Clinton", "Coles", "Cook", "Crawford", "Cumberland",
    "DeKalb", "DeWitt", "Douglas", "DuPage", "Edgar", "Edwards",
    "Effingham", "Fayette", "Ford", "Franklin", "Fulton", "Gallatin",
    "Greene", "Grundy", "Hamilton", "Hancock", "Hardin", "Henderson",
    "Henry", "Iroquois", "Jackson", "Jasper", "Jefferson", "Jersey",
    "Jo Daviess", "Johnson", "Kane", "Kankakee", "Kendall", "Knox",
    "Lake", "LaSalle", "Lawrence", "Lee", "Livingston", "Logan",
    "Macon", "Macoupin", "Madison", "Marion", "Marshall", "Mason",
    "Massac", "McDonough", "McHenry", "McLean", "Menard", "Mercer",
    "Monroe", "Montgomery", "Morgan", "Moultrie", "Ogle", "Peoria",
    "Perry", "Piatt", "Pike", "Pope", "Pulaski", "Putnam",
    "Randolph", "Richland", "Rock Island", "Saline", "Sangamon",
    "Schuyler", "Scott", "Shelby", "St. Clair", "Stark", "Stephenson",
    "Tazewell", "Union", "Vermilion", "Wabash", "Warren",
    "Washington", "Wayne", "White", "Whiteside", "Will",
    "Williamson", "Winnebago", "Woodford"
]

ILLINOIS_CITIES = {
    "Adams": ["Quincy", "Camp Point"],
    "Alexander": ["Cairo", "Tamms"],
    "Bond": ["Greenville", "Pocahontas"],
    "Boone": ["Belvidere", "Poplar Grove"],
    "Brown": ["Mount Sterling", "Ripley"],
    "Bureau": ["Princeton", "Spring Valley"],
    "Calhoun": ["Hardin", "Batchtown"],
    "Carroll": ["Mount Carroll", "Savanna"],
    "Cass": ["Virginia", "Beardstown"],
    "Champaign": ["Champaign", "Urbana", "Savoy"],
    "Christian": ["Taylorville", "Pana"],
    "Clark": ["Marshall", "Westfield"],
    "Clay": ["Flora", "Louisville"],
    "Clinton": ["Carlyle", "Breese"],
    "Coles": ["Charleston", "Mattoon"],
    "Cook": ["Chicago", "Evanston", "Oak Park", "Cicero"],
    "Crawford": ["Robinson", "Palestine"],
    "Cumberland": ["Toledo", "Greenup"],
    "DeKalb": ["DeKalb", "Sycamore"],
    "DeWitt": ["Clinton", "Farmer City"],
    "Douglas": ["Tuscola", "Villa Grove"],
    "DuPage": ["Naperville", "Wheaton", "Downers Grove"],
    "Edgar": ["Paris", "Chrisman"],
    "Edwards": ["Albion", "West Salem"],
    "Effingham": ["Effingham", "Teutopolis"],
    "Fayette": ["Vandalia", "Ramsey"],
    "Ford": ["Paxton", "Gibson City"],
    "Franklin": ["Benton", "West Frankfort"],
    "Fulton": ["Canton", "Lewistown"],
    "Gallatin": ["Shawneetown", "Ridgway"],
    "Greene": ["Carrollton", "White Hall"],
    "Grundy": ["Morris", "Minooka"],
    "Hamilton": ["McLeansboro", "Broughton"],
    "Hancock": ["Carthage", "Nauvoo"],
    "Hardin": ["Elizabethtown", "Rosiclare"],
    "Henderson": ["Oquawka", "Gladstone"],
    "Henry": ["Kewanee", "Geneseo"],
    "Iroquois": ["Watseka", "Gilman"],
    "Jackson": ["Carbondale", "Murphysboro"],
    "Jasper": ["Newton", "Dieterich"],
    "Jefferson": ["Mount Vernon", "Woodlawn"],
    "Jersey": ["Jerseyville", "Grafton"],
    "Jo Daviess": ["Galena", "East Dubuque"],
    "Johnson": ["Vienna", "Buncombe"],
    "Kane": ["Aurora", "Elgin", "Geneva"],
    "Kankakee": ["Kankakee", "Bourbonnais"],
    "Kendall": ["Yorkville", "Plano"],
    "Knox": ["Galesburg", "Abingdon"],
    "Lake": ["Waukegan", "Highland Park", "Libertyville"],
    "LaSalle": ["Ottawa", "Peru", "LaSalle"],
    "Lawrence": ["Lawrenceville", "Bridgeport"],
    "Lee": ["Dixon", "Amboy"],
    "Livingston": ["Pontiac", "Dwight"],
    "Logan": ["Lincoln", "Mount Pulaski"],
    "Macon": ["Decatur", "Forsyth"],
    "Macoupin": ["Carlinville", "Gillespie"],
    "Madison": ["Edwardsville", "Alton", "Granite City"],
    "Marion": ["Salem", "Centralia"],
    "Marshall": ["Lacon", "Henry"],
    "Mason": ["Havana", "Easton"],
    "Massac": ["Metropolis", "Joppa"],
    "McDonough": ["Macomb", "Blandinsville"],
    "McHenry": ["Crystal Lake", "Woodstock"],
    "McLean": ["Bloomington", "Normal"],
    "Menard": ["Petersburg", "Athens"],
    "Mercer": ["Aledo", "New Boston"],
    "Monroe": ["Waterloo", "Columbia"],
    "Montgomery": ["Hillsboro", "Litchfield"],
    "Morgan": ["Jacksonville", "Meredosia"],
    "Moultrie": ["Sullivan", "Lovington"],
    "Ogle": ["Oregon", "Rochelle"],
    "Peoria": ["Peoria", "Chillicothe"],
    "Perry": ["Pinckneyville", "Du Quoin"],
    "Piatt": ["Monticello", "Bement"],
    "Pike": ["Pittsfield", "Griggsville"],
    "Pope": ["Golconda", "Eddyville"],
    "Pulaski": ["Mounds City", "Ullin"],
    "Putnam": ["Hennepin", "Granville"],
    "Randolph": ["Chester", "Red Bud"],
    "Richland": ["Olney", "Noble"],
    "Rock Island": ["Moline", "Rock Island", "East Moline"],
    "Saline": ["Harrisburg", "Eldorado"],
    "Sangamon": ["Springfield", "Chatham"],
    "Schuyler": ["Rushville", "Littleton"],
    "Scott": ["Winchester", "Manchester"],
    "Shelby": ["Shelbyville", "Tower Hill"],
    "St. Clair": ["Belleville", "East St. Louis", "O'Fallon"],
    "Stark": ["Toulon", "Wyoming"],
    "Stephenson": ["Freeport", "Lena"],
    "Tazewell": ["Pekin", "Morton"],
    "Union": ["Anna", "Jonesboro"],
    "Vermilion": ["Danville", "Georgetown"],
    "Wabash": ["Mount Carmel", "Bellmont"],
    "Warren": ["Monmouth", "Roseville"],
    "Washington": ["Nashville", "Okawville"],
    "Wayne": ["Fairfield", "Wayne City"],
    "White": ["Carmi", "Enfield"],
    "Whiteside": ["Sterling", "Rock Falls"],
    "Will": ["Joliet", "Plainfield", "Romeoville"],
    "Williamson": ["Marion", "Herrin"],
    "Winnebago": ["Rockford", "Loves Park"],
    "Woodford": ["Eureka", "El Paso"]
}

def generate_location():
    county = random.choice(ILLINOIS_COUNTIES)
    city = random.choice(ILLINOIS_CITIES.get(county))
    return county, city

def generate_name_with_sex():
    sex = random.choice(["M", "F"])
    
    if sex == "M":
        first = fake.first_name_male()
    else: 
        first = fake.first_name_female()
        
    middle = fake.first_name() if random.random() < 0.7 else ""
    last = fake.last_name()
    
    return sex, first, middle, last

def generate_age_and_death_date():
    age = random.randint(0, 100)
    today = date.today()
    
    birth_year = today.year - age
    birth_end = min(date(birth_year, 12, 31), today)
    birth_date = fake.date_between(start_date=date(birth_year, 1, 1), end_date=birth_end)
    death_date = fake.date_between(start_date=birth_date, end_date=today)
    return age, death_date.isoformat()

def generate_death_record():
    sex, first, middle, last = generate_name_with_sex()
    age, death_date = generate_age_and_death_date()
    county, city = generate_location()
    
    return {
        "last_name": last,
        "first_name": first,
        "middle_name": middle,
        "sex": sex,
        "age": age,
        "death_date": death_date,
        "county": county,
        "city": city
    }


def append_record(record):
    if FILE.exists():
        data = json.loads(FILE.read_text())
    else:
        data = []

    data.append(record)
    FILE.write_text(json.dumps(data, indent=2))
    
if __name__ == "__main__":
    for records in range(NUM_RECORDS):
        append_record(generate_death_record())

