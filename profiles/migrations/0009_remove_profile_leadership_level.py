# Generated by Django 2.2.10 on 2020-05-07 20:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("profiles", "0008_populate_addresses")]

    operations = [migrations.RemoveField(model_name="profile", name="leadership_level")]
