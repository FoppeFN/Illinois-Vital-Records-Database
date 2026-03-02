from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension


class Migration(migrations.Migration):

    initial = True
    dependencies = []

    operations = [
        TrigramExtension(),
    ]