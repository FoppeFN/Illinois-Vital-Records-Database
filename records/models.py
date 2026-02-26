from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.contrib.auth.models import User


#####################################
#          PERSON TABLES            #
#####################################


# defines binary sex choices
class Sex(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    UNKNOWN = 'U', 'Unknown'



# defines counties
class County(models.Model):
    #metadata
    class Meta:
        verbose_name = "County"
        verbose_name_plural = "Counties"
        indexes = [
            GinIndex(fields=["county_name"], name="county_name_trgm", opclasses=["gin_trgm_ops"])
        ]
    
    county_code = models.IntegerField(
        primary_key=True
    )

    county_name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return f"{self.county_code}: {self.county_name}"


# defines cities
class City(models.Model):
    #metadata
    class Meta:
        verbose_name = "City"
        verbose_name_plural = "Cities"
        indexes = [
            GinIndex(fields=["city_name"], name="city_name_trgm", opclasses=["gin_trgm_ops"])
        ]
    
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE,
        related_name="city"
    )

    city_name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return f"{self.city_name} - {self.county}"


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
        indexes = [
            GinIndex(fields=["first_name"], name="person_first_name_trgm", opclasses=["gin_trgm_ops"]),
            GinIndex(fields=["last_name"], name="person_last_name_trgm", opclasses=["gin_trgm_ops"]),
            GinIndex(fields=["middle_name"], name="person_middle_name_trgm", opclasses=["gin_trgm_ops"])
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
        return f"{self.last_name}, {self.first_name} {self.middle_name}"
    
    # find children by obtaining all people with self as parent
    def children(self, child_sex=None):
        qs = Person.objects.filter(models.Q(mother=self) | models.Q(father=self))
        if child_sex:
            qs = qs.filter(sex=child_sex)
        return qs
    
    def sons(self):
        return self.children(Sex.MALE)
    
    def daughters(self):
        return self.children(Sex.FEMALE)
    
    # find siblings by obtaining all people with same parent as self
    def siblings(self, sibling_sex=None):
        qs = Person.objects.filter(models.Q(mother=self.mother) | models.Q(father=self.father))
        if sibling_sex:
            qs = qs.filter(sex=sibling_sex)
        return qs.exclude(id=self.id)
    
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

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="birth"
    )

    birth_date = models.DateField(blank=True, null=True)

    birth_county = models.ForeignKey(
        County,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    birth_city = models.ForeignKey(
        City,
        blank = True,
        null = True,
        on_delete=models.SET_NULL
    )

    birth_record_image = models.ImageField(
        upload_to = 'birth_records/',
        blank = True,
        null = True
    )

    def __str__(self):
        return f"{self.person}: {self.birth_date}"





class Death(models.Model):

    # metadata
    class Meta:
        verbose_name = "Death"
        verbose_name_plural = "Deaths"
        ordering = [
            'death_date',
            'death_county'
        ]

    person = models.ForeignKey(
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
    
    death_county = models.ForeignKey(
        County,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )

    death_city = models.ForeignKey(
        City,
        blank = True,
        null = True,
        on_delete=models.SET_NULL
    )

    death_record_image = models.ImageField(
        upload_to = 'death_records/',
        blank = True,
        null = True
    )

    def __str__(self):
        return f"{self.person}: {self.death_date}"




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
    marriage_county = models.ForeignKey(
        County,
        blank = True,
        null = True,
        on_delete=models.SET_NULL
    )

    marriage_city = models.ForeignKey(
        City,
        blank = True,
        null = True,
        on_delete=models.SET_NULL
    )

    #divorce_date = models.DateField(null=True, blank=True)

    marriage_record_image = models.ImageField(
        upload_to = 'marriage_records/',
        blank = True,
        null = True
    )

    def __str__(self):
        return f"{self.spouse1} & {self.spouse2}: {self.marriage_date}"
    
    # prevents duplicate marriages
    def save(self, *args, **kwargs):
        if self.spouse2.id < self.spouse1.id:
            self.spouse1, self.spouse2 = self.spouse2, self.spouse1
        super().save(*args, **kwargs)



#################################
#         COMMENT MODELS        #
#################################



class Comment(models.Model):

    # metadata
    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['-creation_time']

    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE
    )

    # comment content
    comment_content = models.CharField(max_length=2000)
    creation_time = models.DateTimeField()

    # user optional content
    commenter_name = models.CharField(max_length=100, blank=True, null=True)
    commenter_email = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.person}: {self.creation_time}"