# Generated by Django 2.2.13 on 2020-08-12 20:58

from django.db import migrations


def generate_bootcamp_run_id(apps, schema_editor):
    Line = apps.get_model("ecommerce", "Line")
    BootcampRun = apps.get_model("klasses", "BootcampRun")

    for line in Line.objects.all():
        run = BootcampRun.objects.filter(run_key=line.run_key).first()
        line.bootcamp_run = run
        line.save()


class Migration(migrations.Migration):
    dependencies = [("ecommerce", "0006_line_bootcamp_run")]

    operations = [
        migrations.RunPython(
            generate_bootcamp_run_id, reverse_code=migrations.RunPython.noop
        )
    ]
