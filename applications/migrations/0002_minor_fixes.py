# Generated by Django 2.2.10 on 2020-05-05 20:27

import applications.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0001_bootcamp_application_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bootcampapplication',
            name='resume_file',
            field=models.FileField(blank=True, null=True, upload_to=applications.models._get_resume_upload_path),
        ),
        migrations.AlterUniqueTogether(
            name='applicationstepsubmission',
            unique_together={('bootcamp_application', 'run_application_step')},
        ),
    ]