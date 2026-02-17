from django.db.models import Q
from django.db.models.expressions import RawSQL
from records.models import Person, Birth, Marriage, Death, Sex

class BaseRecordSearch:

    @staticmethod
    def _build_q(filters: dict, table_name: str, related_prefix = ""):
        q = Q()

        for field, value in filters.items():
            if value is None or value == "":
                continue
        
            if field == "sex" and value in Sex.values:
                q &= Q(**{f"{related_prefix}sex": value})
                continue

            # wildcards
            if "%" in str(value) or "_" in str(value):
                sql = f"SELECT id FROM {table_name} WHERE {field} LIKE %s"
                q &= Q(**{f"id__in": RawSQL(sql, [value])})
            else:
                q &= Q(**{f"{related_prefix}{field}__icontains": value})

        return q
    


class BirthRecordSearch(BaseRecordSearch):
    
    @staticmethod
    def search(filters: dict):
        qs = Birth.objects.select_related("person")
        q = Q()

        person_fields = [f.name for f in Person._meta.get_fields() 
                 if f.concrete and f.name not in ["id", "mother", "father"]]
        birth_fields = [f.name for f in Birth._meta.get_fields()
                 if f.concrete and f.name not in ["id", "person"]]
        
        person_filters = {k: v for k, v in filters if k in person_fields}
        birth_filters = {k: v for k, v in filters if k in birth_fields}

        q &= BaseRecordSearch._build_q(person_filters, "records_person", related_prefix="person__")
        q &= BaseRecordSearch._build_q(birth_filters, "records_birth")

        return qs.filter(q).distinct()
    


class DeathRecordSearch(BaseRecordSearch):
    
    @staticmethod
    def search(filters: dict):
        qs = Birth.objects.select_related("person")
        q = Q()

        person_fields = [f.name for f in Person._meta.get_fields() 
                 if f.concrete and f.name not in ["id", "mother", "father"]]
        death_fields = [f.name for f in Death._meta.get_fields()
                 if f.concrete and f.name not in ["id", "person"]]
        
        person_filters = {k: v for k, v in filters if k in person_fields}
        death_filters = {k: v for k, v in filters if k in death_fields}

        q &= BaseRecordSearch._build_q(person_filters, "records_person", related_prefix="person__")
        q &= BaseRecordSearch._build_q(death_filters, "records_death")

        return qs.filter(q).distinct()
    



# TODO: MARRIAGERECORDSEARCH