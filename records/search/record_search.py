from records.models import Person, Birth, Death, Marriage, County, City
from django.db.models import CharField, TextField, DateField
from django.db import connection
import re
from django.db.models import Q



# HELPERS ============

def _wild_clean(filters: dict) -> dict:
    esc = {}
    for k, v in filters.items():
        escaped = re.escape(v)
        escaped = escaped.replace("%", ".*")
        escaped = escaped.replace("_", ".")
        esc[k] = f"^{escaped}$"
    return esc

def _get_model_filters(filters: dict, model):
    rv = {}
    fields_model = {f.name for f in model._meta.concrete_fields if isinstance(f, (CharField, TextField))}
    for k, v in filters.items():
        if k in fields_model:
            rv[k] = v
    return rv

def _get_date_and_variance(filters, field_name):
    if field_name in filters:
        return int(filters[field_name]), int(filters.get("variance", 0))
    return None, None

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

def birth_search(filters: dict, fuzzy: bool = False):
    filters_birth = _wild_clean(_get_birth_filters(filters))
    filters_county = _wild_clean(_get_county_filters(filters))
    filters_city = _wild_clean(_get_city_filters(filters))

    q = Q()

    # Birth fields
    for field, pattern in filters_birth.items():
        q &= Q(**{f"{field}__iregex": pattern})

    # Person fields (JOIN)
    if fuzzy:
        q &= _fuzzy_person_search(filters.get("first_name"), filters.get("middle_name"), filters.get("last_name"))
    else:
        filters_person = _wild_clean(_get_person_filters(filters))
        for field, pattern in filters_person.items():
            q &= Q(**{f"person__{field}__iregex": pattern})

    # County JOIN
    for field, pattern in filters_county.items():
        q &= Q(**{f"birth_county__{field}__iregex": pattern})

    # City JOIN
    for field, pattern in filters_city.items():
        q &= Q(**{f"birth_city__{field}__iregex": pattern})

    birth_date, variance = _get_date_and_variance(filters, "birth_date")

    if birth_date is not None:
        s, e = _get_date_range(birth_date, variance)
        q &= Q(birth_date__year__gte=s, birth_date__year__lte=e)

    return Birth.objects.filter(q).distinct()



def death_search(filters: dict, fuzzy: bool = False):
    filters_death = _wild_clean(_get_death_filters(filters))
    filters_county = _wild_clean(_get_county_filters(filters))
    filters_city = _wild_clean(_get_city_filters(filters))

    q = Q()

    # Death fields
    for field, pattern in filters_death.items():
        q &= Q(**{f"{field}__iregex": pattern})

    # Person fields (JOIN)
    if fuzzy:
        q &= _fuzzy_person_search(filters.get("first_name"), filters.get("middle_name"), filters.get("last_name"))
    else:
        filters_person = _wild_clean(_get_person_filters(filters))
        for field, pattern in filters_person.items():
            q &= Q(**{f"person__{field}__iregex": pattern})

    # County JOIN
    for field, pattern in filters_county.items():
        q &= Q(**{f"death_county__{field}__iregex": pattern})

    # City JOIN
    for field, pattern in filters_city.items():
        q &= Q(**{f"death_city__{field}__iregex": pattern})

    death_date, variance = _get_date_and_variance(filters, "death_date")

    if death_date is not None:
        s, e = _get_date_range(death_date, variance)
        q &= Q(death_date__year__gte=s, death_date__year__lte=e)

    return Death.objects.filter(q).distinct()



def marriage_search(filters: dict, fuzzy1: bool = False, fuzzy2: bool = False):
    filters_marriage = _wild_clean(_get_marriage_filters(filters))
    filters_spouse1, filters_spouse2 = _marriage_to_person_filters(filters)
    filters_spouse1 = _wild_clean(filters_spouse1)
    filters_spouse2 = _wild_clean(filters_spouse2)
    filters_county = _wild_clean(_get_county_filters(filters))
    filters_city = _wild_clean(_get_city_filters(filters))

    q = Q()

    # Marriage fields
    for field, pattern in filters_marriage.items():
        q &= Q(**{f"{field}__iregex": pattern})

    for field, pattern in filters_county.items():
        q &= Q(**{f"marriage_county__{field}__iregex": pattern})

    for field, pattern in filters_city.items():
        q &= Q(**{f"marriage_city__{field}__iregex": pattern})

    q_s1_set1 = Q()
    q_s2_set2 = Q()
    q_s1_set2 = Q()
    q_s2_set1 = Q()

    # spouse 1
    if fuzzy1:
        q_s1_set1 &= _fuzzy_person_search(
            filters_spouse1.get("first_name"),
            filters_spouse1.get("middle_name"),
            filters_spouse1.get("last_name"),
            "spouse1__"
        )
        q_s1_set2 &= _fuzzy_person_search(
            filters_spouse2.get("first_name"),
            filters_spouse2.get("middle_name"),
            filters_spouse2.get("last_name"),
            "spouse1__"
        )
    else:
        for field, pattern in filters_spouse1.items():
            q_s1_set1 &= Q(**{f"spouse1__{field}__iregex": pattern})
        for field, pattern in filters_spouse2.items():
            q_s1_set2 &= Q(**{f"spouse1__{field}__iregex": pattern})
    
    # spouse 2
    if fuzzy2:
        q_s2_set2 &= _fuzzy_person_search(
            filters_spouse2.get("first_name"),
            filters_spouse2.get("middle_name"),
            filters_spouse2.get("last_name"),
            "spouse2__"
        )
        q_s2_set1 &= _fuzzy_person_search(
            filters_spouse1.get("first_name"),
            filters_spouse1.get("middle_name"),
            filters_spouse1.get("last_name"),
            "spouse2__"
        )
    else:
        for field, pattern in filters_spouse2.items():
            q_s2_set2 &= Q(**{f"spouse2__{field}__iregex": pattern})
        for field, pattern in filters_spouse1.items():
            q_s2_set1 &= Q(**{f"spouse2__{field}__iregex": pattern})

    q_order1 = q_s1_set1 & q_s2_set2
    q_order2 = q_s1_set2 & q_s2_set1

    q &= (q_order1 | q_order2)

    marriage_date, variance = _get_date_and_variance(filters, "marriage_date")

    if marriage_date is not None:
        s, e = _get_date_range(marriage_date, variance)
        q &= Q(marriage_date__year__gte=s, marriage_date__year__lte=e)

    return Marriage.objects.filter(q).distinct()

def _fuzzy_person_search(first_name: str, middle_name: str, last_name: str, prefix: str = "person__"):
    with connection.cursor() as cursor:
        cursor.execute("SET pg_trgm.similarity_threshold = 0.25;")

    q = Q()

    if first_name:
        q &= Q(**{f"{prefix}first_name__trigram_similar": first_name})
    if middle_name:
        q &= Q(**{f"{prefix}middle_name__trigram_similar": middle_name})
    if last_name:
        q &= Q(**{f"{prefix}last_name__trigram_similar": last_name})

    return q

def narrow_down(query: str, objects):
    if not query:
        return objects

    model = objects.model
    q = Q()

    for field in model._meta.get_fields():

        # Direct text fields
        if isinstance(field, (CharField, TextField, DateField)):
            q |= Q(**{f"{field.name}__icontains": query})

        # ForeignKey relations (1 level deep)
        if field.is_relation and field.many_to_one:
            rel_model = field.related_model
            for rel_field in rel_model._meta.get_fields():
                if rel_field.concrete and isinstance(rel_field, (CharField, TextField)):
                    q |= Q(**{
                        f"{field.name}__{rel_field.name}__icontains": query
                    })

    return objects.filter(q).distinct()