from django.contrib import admin
from .models import Person, Birth, Death, Marriage, County, City, Comment

# Register your models here.
admin.site.register(Person)
admin.site.register(Birth)
admin.site.register(Death)
admin.site.register(Marriage)
admin.site.register(County)
admin.site.register(City)
admin.site.register(Comment)