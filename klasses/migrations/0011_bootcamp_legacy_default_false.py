# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-12-13 18:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("klasses", "0010_bootcamp_legacy")]

    operations = [
        migrations.AlterField(
            model_name="bootcamp",
            name="legacy",
            field=models.BooleanField(default=False),
        )
    ]
