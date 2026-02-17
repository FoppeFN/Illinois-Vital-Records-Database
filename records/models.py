from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from .utils import load_county_choices

COUNTIES = load_county_choices()



# defines binary sex choices
class Sex(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    UNKNOWN = 'U', 'Unknown'



# Create your models here.
class Person(models.Model):
    # metadata
    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = [
            'last_name',
            'first_name',
            'middle_name',
            'sex'
        ]

    # BASIC ===========================================
    # name
    last_name = models.CharField(max_length = 100, blank=True, null=True)
    first_name = models.CharField(max_length = 100, blank=True, null=True)
    middle_name = models.CharField(max_length = 100, blank=True, null=True)
    
    # sex
    sex = models.CharField(
        max_length = 1,
        choices = Sex.choices,
        blank=True,
        null=True
    )
    # =================================================

    # RELATIONS =======================================
    mother = models.ForeignKey(
        "self",
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "children_from_mother"
    )

    father = models.ForeignKey(
        "self",
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "children_from_father"
    )
    # ==================================================

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    # find children by obtaining all people with self as parent
    def children(self, child_sex=None):
        qs = Person.objects.filter(models.Q(mother=self) | models.Q(father=self))
        if child_sex in Sex.values:
            qs = qs.filter(sex=child_sex)
        return qs
    
    def sons(self):
        return self.children(Sex.MALE)
    
    def daughters(self):
        return self.children(Sex.FEMALE)
    
    # find siblings by obtaining all people with same parent as self
    def siblings(self, sibling_sex=None):
        qs = Person.objects.filter(models.Q(mother=self.mother) | models.Q(father=self.father))
        if sibling_sex in Sex.values:
            qs = qs.filter(sex=sibling_sex)
        return qs
    
    def brothers(self):
        return self.siblings(Sex.MALE)
    
    def sisters(self):
        return self.siblings(Sex.FEMALE)
    

    




class Birth(models.Model):

    # metadata
    class Meta:
        verbose_name = "Birth"
        verbose_name_plural = "Births"
        ordering = [
            'birth_date',
            'birth_county'
        ]

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="birth"
    )

    birth_date = models.DateField(blank=True, null=True)

    birth_county = models.CharField(
        max_length=3,
        choices = COUNTIES,    # grab counties from CSV
        blank=True,
        null=True
    )

    birth_city = models.CharField(
        max_length = 50,
        blank = True,
        null = True
    )

    birth_record_image = models.ImageField(
        upload_to = 'birth_records/',
        blank = True,
        null = True
    )





class Death(models.Model):

    # metadata
    class Meta:
        verbose_name = "Death"
        verbose_name_plural = "Deaths"
        ordering = [
            'death_date',
            'death_county'
        ]

    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="death"
    )

    death_date = models.DateField(blank=True, null=True)

    death_age = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(150),
        ]
    )
    
    death_county = models.CharField(
        max_length=3,
        choices = COUNTIES,    # grab counties from CSV
        blank=True,
        null=True
    )

    death_city = models.CharField(
        max_length = 50,
        blank = True,
        null = True
    )

    death_record_image = models.ImageField(
        upload_to = 'death_records/',
        blank = True,
        null = True
    )




class Marriage(models.Model):

    # metadata
    class Meta:
        verbose_name = "Marriage"
        verbose_name_plural = "Marriages"
        ordering = ['marriage_date', 'marriage_county']
        constraints = [
            models.UniqueConstraint(
                fields = ['spouse1', 'spouse2', 'marriage_date'],
                name = "unique_marriages"
            )
        ]

    spouse1 = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        related_name = "marriages_as_spouse1"
    )

    spouse2 = models.ForeignKey(
        Person,
        on_delete = models.CASCADE,
        related_name = "marriages_as_spouse2"
    )

    marriage_date = models.DateField(null=True, blank=True)
    marriage_county = models.CharField(
        max_length=3,
        choices = COUNTIES,
        blank = True,
        null = True
    )

    marriage_city = models.CharField(
        max_length = 50,
        blank = True,
        null = True
    )

    divorce_date = models.DateField(null=True, blank=True)

    marriage_record_image = models.ImageField(
        upload_to = 'marriage_records/',
        blank = True,
        null = True
    )

    def __str__(self):
        return f"{self.spouse1} & {self.spouse2} {self.marriage_date}"
    
    # prevents duplicate marriages
    def save(self, *args, **kwargs):
        if self.spouse2.id < self.spouse1.id:
            self.spouse1, self.spouse2 = self.spouse2, self.spouse1
        super().save(*args, **kwargs)