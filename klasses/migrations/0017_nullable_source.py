# Generated by Django 2.2.10 on 2020-05-11 15:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("klasses", "0016_bootcamprunenrollment")]

    operations = [
        migrations.AlterField(
            model_name="bootcamprun",
            name="source",
            field=models.CharField(
                blank=True,
                choices=[
                    (None, None),
                    ("SMApply", "SMApply"),
                    ("FluidRev", "FluidRev"),
                ],
                default=None,
                max_length=10,
                null=True,
            ),
        )
    ]
