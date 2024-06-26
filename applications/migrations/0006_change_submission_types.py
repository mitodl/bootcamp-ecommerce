# Generated by Django 2.2.10 on 2020-05-11 16:06

from django.db import migrations, models


def update_submission_types(apps, schema_editor):
    """
    Updates submission_type values in ApplicationStep to new values
    """
    ApplicationStep = apps.get_model("applications", "ApplicationStep")
    ApplicationStep.objects.filter(submission_type="video_interview").update(
        submission_type="videointerviewsubmission"
    )
    ApplicationStep.objects.filter(submission_type="quiz").update(
        submission_type="quizsubmission"
    )


def undo_update_submission_types(apps, schema_editor):
    """
    Updates submission_type values in ApplicationStep to old values
    """
    ApplicationStep = apps.get_model("applications", "ApplicationStep")
    ApplicationStep.objects.filter(submission_type="videointerviewsubmission").update(
        submission_type="video_interview"
    )
    ApplicationStep.objects.filter(submission_type="quizsubmission").update(
        submission_type="quiz"
    )


class Migration(migrations.Migration):
    dependencies = [("applications", "0005_application_multiple_orders")]

    operations = [
        migrations.AlterField(
            model_name="applicationstep",
            name="submission_type",
            field=models.CharField(
                choices=[
                    ("videointerviewsubmission", "Video Interview"),
                    ("quizsubmission", "Quiz"),
                    ("video_interview", "video_interview"),
                    ("quiz", "quiz"),
                ],
                max_length=40,
            ),
        ),
        migrations.RunPython(update_submission_types, undo_update_submission_types),
        migrations.AlterField(
            model_name="applicationstep",
            name="submission_type",
            field=models.CharField(
                choices=[
                    ("videointerviewsubmission", "Video Interview"),
                    ("quizsubmission", "Quiz"),
                ],
                max_length=40,
            ),
        ),
    ]
