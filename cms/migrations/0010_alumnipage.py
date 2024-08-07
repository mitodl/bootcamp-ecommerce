# Generated by Django 2.2.10 on 2020-05-27 08:00

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0001_squashed_0021"),
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
        ("cms", "0009_sitenotification"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlumniPage",
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
                        default="Alumni",
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
                    "alumni_bios",
                    wagtail.fields.StreamField(
                        [
                            (
                                "alumni",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                help_text="The image of the alumni"
                                            ),
                                        ),
                                        (
                                            "name",
                                            wagtail.blocks.CharBlock(
                                                help_text="Name of the alumni.",
                                                max_length=100,
                                            ),
                                        ),
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                help_text="The title to display after the name.",
                                                max_length=255,
                                            ),
                                        ),
                                        (
                                            "class_text",
                                            wagtail.blocks.CharBlock(
                                                help_text="A brief description about the alumni class.",
                                                max_length=100,
                                            ),
                                        ),
                                        (
                                            "quote",
                                            wagtail.blocks.RichTextBlock(
                                                help_text="The quote that appears on the alumni section."
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        help_text="Alumni to display in this section.",
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
            options={"verbose_name": "Alumni Section"},
            bases=("wagtailcore.page",),
        )
    ]
