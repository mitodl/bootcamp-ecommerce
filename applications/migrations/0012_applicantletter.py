# Generated by Django 2.2.13 on 2020-06-24 20:08

from django.db import migrations, models
import django.db.models.deletion
import uuid
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0011_applicationstepsubmission_submission_status")
    ]

    operations = [
        migrations.CreateModel(
            name="ApplicantLetter",
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
                ("is_acceptance", models.BooleanField()),
                ("letter_subject", models.TextField()),
                ("letter_text", wagtail.core.fields.RichTextField()),
                ("hash", models.UUIDField(default=uuid.uuid4, unique=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="applications.BootcampApplication",
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]