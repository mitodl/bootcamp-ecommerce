# Generated by Django 2.2.13 on 2021-03-29 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("profiles", "0009_remove_profile_leadership_level")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="can_skip_application_steps",
            field=models.BooleanField(default=False),
        )
    ]