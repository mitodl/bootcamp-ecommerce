# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-23 17:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("profiles", "0004_profile_smapply_user_data")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="smapply_demographic_data",
            field=models.JSONField(blank=True, null=True),
        )
    ]
