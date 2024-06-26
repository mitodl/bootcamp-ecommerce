# Generated by Django 2.2.10 on 2020-06-15 11:53

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
        ("wagtailimages", "0001_squashed_0021"),
        ("cms", "0016_admissions_section"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeAlumniPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.Page",
                    ),
                ),
                (
                    "heading",
                    models.CharField(
                        help_text="The heading to display on this section.",
                        max_length=100,
                    ),
                ),
                (
                    "text",
                    wagtail.fields.RichTextField(
                        help_text="Extra text to appear besides alumni quotes in this section."
                    ),
                ),
                (
                    "highlight_quote",
                    models.CharField(
                        help_text="Highlighted quote to display for this section.",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "highlight_name",
                    models.CharField(
                        help_text="Name of the alumni for the highlighted quote.",
                        max_length=100,
                    ),
                ),
                (
                    "banner_image",
                    models.ForeignKey(
                        help_text="Image that will display as a banner at the top of the section, must be at least 750x505 pixels.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.Image",
                    ),
                ),
            ],
            options={"verbose_name": "Homepage Alumni Section"},
            bases=("wagtailcore.page",),
        )
    ]
