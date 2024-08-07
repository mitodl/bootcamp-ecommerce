# Generated by Django 2.2.18 on 2021-04-26 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("klasses", "0025_bootcamprun_allows_skipped_steps"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bootcamprunenrollment",
            name="change_status",
            field=models.CharField(
                blank=True,
                choices=[("deferred", "deferred"), ("refunded", "refunded")],
                max_length=20,
                null=True,
            ),
        ),
        migrations.CreateModel(
            name="BootcampRunEnrollmentAudit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                ("updated_on", models.DateTimeField(auto_now=True)),
                (
                    "data_before",
                    models.JSONField(blank=True, null=True),
                ),
                (
                    "data_after",
                    models.JSONField(blank=True, null=True),
                ),
                (
                    "acting_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "enrollment",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="klasses.BootcampRunEnrollment",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
