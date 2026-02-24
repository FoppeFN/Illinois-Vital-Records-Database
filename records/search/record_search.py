from records.models import Person, Birth, Death, Marriage, County, City
import re
from django.db.models import Q



# HELPERS ============

def _wild_clean(filters: dict) -> dict:
    esc = {}
    for k, v in filters.items():
        escaped = re.escape(v)
        escaped = escaped.replace(r"\.\*", ".*")
        escaped = escaped.replace(r"\.", ".")
        esc[k] = f"^{escaped}$"
    return esc

def _build_search_with_filters(filters: dict):
    q = Q()
    for field, pattern in filters.items():
        q &= Q(**{f"{field}__iregex": pattern})
    return q

def _get_model_filters(filters: dict, model):
    rv = {}
    fields_model = {f.name for f in model._meta.concrete_fields if "date" not in f}
    for k, v in filters.items():
        if k in fields_model:
            rv[k] = v
    return rv

def _get_date_and_variance(filters: dict) -> tuple[int, int]:
    for k, v in filters.items():
        if "date" in k:
            return int(v), int(filters.get("variance", 0))
    return None, None

def _build_birth_date_search(d: int, variance: int):
    s, e = _get_date_range(d, variance)
    return Q(birth_date__year__gte=s, birth_date__year__lte=e)

def _build_death_date_search(d: int, variance: int):
    s, e = _get_date_range(d, variance)
    return Q(death_date__year__gte=s, death_date__year__lte=e)

def _build_marriage_date_search(d: int, variance: int):
    s, e = _get_date_range(d, variance)
    return Q(marriage_date__year__gte=s, marriage_date__year__lte=e)

def _marriage_to_person_filters(filters: dict) -> tuple[dict, dict]:
    filters_spouse1 = {}
    filters_spouse2 = {}
    for k, v in filters.items():
        if "spouse1" in k:
            _, _, k_person = k.partition("spouse1_")
            filters_spouse1[k_person] = v
        if "spouse2" in k:
            _, _, k_person = k.partition("spouse2_")
            filters_spouse2[k_person] = v
    return _get_person_filters(filters_spouse1), _get_person_filters(filters_spouse2)

def _get_date_range(d, variance) -> tuple[int, int]:
    s = d - variance
    e = d + variance
    return s, e

def _get_person_filters(filters: dict): return _get_model_filters(filters, Person)
def _get_birth_filters(filters: dict): return _get_model_filters(filters, Birth)
def _get_death_filters(filters: dict): return _get_model_filters(filters, Death)
def _get_marriage_filters(filters: dict): return _get_model_filters(filters, Marriage)
def _get_county_filters(filters: dict): return _get_model_filters(filters, County)
def _get_city_filters(filters: dict): return _get_model_filters(filters, City)



# SEARCH =================

def birth_search(filters: dict):
    filters_person = _get_person_filters(filters)
    filters_birth = _get_birth_filters(filters)
    filters_county = _get_county_filters(filters)
    filters_city = _get_city_filters(filters)

    birth_date, variance = _get_date_and_variance(filters)

    filters_person_esc = _wild_clean(filters_person)
    filters_birth_esc = _wild_clean(filters_birth)
    
    q_person = _build_search_with_filters(filters_person_esc)
    q_birth = _build_search_with_filters(filters_birth_esc)
    q_county = _build_search_with_filters(filters_county)
    q_city = _build_search_with_filters(filters_city)

    q_pcc = q_person & Q(county__in=County.objects.filter(q_county)) & Q(city__in=City.objects.filter(q_city))

    q_combined = q_birth & Q(person__in=Person.objects.filter(q_pcc))

    if birth_date:
        q_combined &= _build_birth_date_search(birth_date, variance)

    return Birth.objects.filter(q_combined)



def death_search(filters: dict):
    filters_person = _get_person_filters(filters)
    filters_death = _get_death_filters(filters)
    filters_county = _get_county_filters(filters)
    filters_city = _get_city_filters(filters)

    death_date, variance = _get_date_and_variance(filters)

    filters_person_esc = _wild_clean(filters_person)
    filters_death_esc = _wild_clean(filters_death)

    q_person = _build_search_with_filters(filters_person_esc)
    q_death = _build_search_with_filters(filters_death_esc)
    q_county = _build_search_with_filters(filters_county)
    q_city = _build_search_with_filters(filters_city)

    q_pcc = q_person & Q(county__in=County.objects.filter(q_county)) & Q(city__in=City.objects.filter(q_city))

    q_combined = q_death & Q(person__in=Person.objects.filter(q_pcc))

    if death_date:
        q_combined &= _build_birth_date_search(death_date, variance)

    return Death.objects.filter(q_combined)



def marriage_search(filters: dict):
    filters_marriage = _get_marriage_filters(filters)
    filters_spouse1, filters_spouse2 = _marriage_to_person_filters(filters)
    filters_county1 = _get_county_filters(filters_spouse1)
    filters_county2 = _get_county_filters(filters_spouse2)
    filters_city1 = _get_city_filters(filters_spouse1)
    filters_city2 = _get_city_filters(filters_spouse2)

    marriage_date, variance = _get_date_and_variance(filters)

    filters_marriage_esc = _wild_clean(filters_marriage)
    filters_spouse1_esc = _wild_clean(filters_spouse1)
    filters_spouse2_esc = _wild_clean(filters_spouse2)

    q_marriage = _build_search_with_filters(filters_marriage_esc)
    q_spouse1 = _build_search_with_filters(filters_spouse1_esc)
    q_spouse2 = _build_search_with_filters(filters_spouse2_esc)
    q_county1 = _build_search_with_filters(filters_county1)
    q_county2 = _build_search_with_filters(filters_county2)
    q_city1 = _build_search_with_filters(filters_city1)
    q_city2 = _build_search_with_filters(filters_city2)

    q_pcc1 = q_spouse1 & Q(county__in=County.objects.filter(q_county1)) & Q(city__in=City.objects.filter(q_city1))
    q_pcc2 = q_spouse2 & Q(county__in=County.objects.filter(q_county2)) & Q(city__in=City.objects.filter(q_city2))

    # Order 1: spouse1 matches first set, spouse2 matches second set
    q_order1 = Q(spouse1__in=Person.objects.filter(q_pcc1)) & Q(spouse2__in=Person.objects.filter(q_pcc2))

    # Order 2: spouse1 matches second set, spouse2 matches first set
    q_order2 = Q(spouse1__in=Person.objects.filter(q_pcc2)) & Q(spouse2__in=Person.objects.filter(q_pcc1))

    q_spouses = q_order1 | q_order2

    q_combined = q_marriage & q_spouses

    if marriage_date:
        q_combined &= _build_marriage_date_search(marriage_date, variance)

    return Marriage.objects.filter(q_combined)