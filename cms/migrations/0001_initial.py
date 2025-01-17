# Generated by Django 2.2.10 on 2020-04-21 17:40

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailimages", "0001_squashed_0021"),
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
    ]

    operations = [
        migrations.CreateModel(
            name="BootcampPage",
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
                    "description",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="The description shown on the product page",
                    ),
                ),
                (
                    "content",
                    wagtail.fields.StreamField(
                        [("rich_text", wagtail.blocks.RichTextBlock())],
                        blank=True,
                        help_text="The content of the benefits page",
                    ),
                ),
                (
                    "thumbnail_image",
                    models.ForeignKey(
                        blank=True,
                        help_text="Thumbnail size must be at least 690x530 pixels.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.Image",
                    ),
                ),
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        )
    ]
