# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-16 19:47
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("klasses", "0006_removed_installment_number")]

    operations = [
        migrations.AlterUniqueTogether(
            name="installment", unique_together=set([("klass", "deadline")])
        ),
        migrations.AlterIndexTogether(
            name="installment", index_together=set([("klass", "deadline")])
        ),
    ]
