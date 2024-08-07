# Generated by Django 2.2.10 on 2020-06-10 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0045_assign_unlock_grouppagepermission"),
        ("cms", "0017_home_page_alumni_section"),
    ]

    operations = [
        migrations.CreateModel(
            name="BootcampIndexPage",
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
                )
            ],
            options={"abstract": False},
            bases=("wagtailcore.page",),
        )
    ]
