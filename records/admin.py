from django.contrib import admin
from .models import Person, Birth, Death, Marriage, County, City, Comment

# Register your models here.

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields = [
        "last_name",
        "first_name",
        "middle_name"
    ]

@admin.register(Birth)
class BirthAdmin(admin.ModelAdmin):
    search_fields = [
        "person__last_name",
        "person__first_name",
        "person__middle_name",
        "birth_date",
        "birth_county__county_code",
        "birth_county__county_name",
        "birth_city__city_name"
    ]

@admin.register(Death)
class DeathAdmin(admin.ModelAdmin):
    search_fields = [
        "person__last_name",
        "person__first_name",
        "person__middle_name",
        "death_date",
        "death_county__county_code",
        "death_county__county_name",
        "death_city__city_name"
    ]

@admin.register(Marriage)
class MarriageAdmin(admin.ModelAdmin):
    search_fields = [
        "spouse1__last_name",
        "spouse1__first_name",
        "spouse1__middle_name",
        "spouse2__last_name",
        "spouse2__first_name",
        "spouse2__middle_name",
        "marriage_date",
        "marriage_county__county_code",
        "marriage_county__county_name",
        "marriage_city__city_name"
    ]

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    search_fields = [
        "county_code",
        "county_name"
    ]

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = [
        "county__county_code",
        "county__county_name",
        "city_name"
    ]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = [
        "comment_name",
        "comment_email"
    ]