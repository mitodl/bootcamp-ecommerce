# Generated by Django 2.2.10 on 2020-05-13 10:30

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
        ("cms", "0007_instructorspage"),
    ]

    operations = [
        migrations.CreateModel(
            name="ThreeColumnImageTextPage",
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
                    "column_image_text_section",
                    wagtail.fields.StreamField(
                        [
                            (
                                "column_image_text_section",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "heading",
                                            wagtail.blocks.CharBlock(
                                                help_text="Heading that will highlight the main point.",
                                                max_length=100,
                                            ),
                                        ),
                                        (
                                            "sub_heading",
                                            wagtail.blocks.CharBlock(
                                                help_text="Area sub heading.",
                                                max_length=250,
                                            ),
                                        ),
                                        ("body", wagtail.blocks.RichTextBlock()),
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                help_text="image size must be at least 150x50 pixels."
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        help_text="Enter detail about area upto max 3 blocks.",
                        null=True,
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        )
    ]
