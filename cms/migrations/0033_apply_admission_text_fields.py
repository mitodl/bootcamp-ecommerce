# Generated by Django 2.2.24 on 2021-11-08 13:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cms", "0032_make_certificate_signatory_images_mandatory"),
    ]

    operations = [
        migrations.AddField(
            model_name="admissionssection",
            name="apply_now_button_text",
            field=models.CharField(
                default="Apply Now", help_text="Apply now button text", max_length=255
            ),
        ),
        migrations.AddField(
            model_name="admissionssection",
            name="how_to_link_text",
            field=models.CharField(
                default="Admissions", help_text="How to title link text", max_length=255
            ),
        ),
        migrations.AddField(
            model_name="admissionssection",
            name="how_to_title",
            field=models.CharField(
                default="How to Apply", help_text="How to title", max_length=255
            ),
        ),
    ]
