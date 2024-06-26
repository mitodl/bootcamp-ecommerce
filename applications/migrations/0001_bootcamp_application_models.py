# Generated by Django 2.2.10 on 2020-05-04 19:04
from uuid import uuid4

import applications.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_fsm


def _get_video_file_path(instance, filename):  # pylint: disable=unused-argument
    """
    Produces the file path for an uploaded video interview

    Return:
         str: The file path
    """
    return f"video_interviews/{uuid4()}_{filename}"


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("klasses", "0014_no_max_len_application_stage"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("ecommerce", "0003_rename_line_klass_id_to_klass_key"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ApplicationStep",
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
                ("step_order", models.PositiveSmallIntegerField(default=1)),
                (
                    "submission_type",
                    models.CharField(
                        choices=[
                            ("video_interview", "video_interview"),
                            ("quiz", "quiz"),
                        ],
                        max_length=30,
                    ),
                ),
                (
                    "bootcamp",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="application_steps",
                        to="klasses.Bootcamp",
                    ),
                ),
            ],
            options={
                "ordering": ["bootcamp", "step_order"],
                "unique_together": {("bootcamp", "step_order")},
            },
        ),
        migrations.CreateModel(
            name="QuizSubmission",
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
                ("submitted_date", models.DateTimeField(blank=True, null=True)),
                (
                    "review_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("approved", "approved"),
                            ("rejected", "rejected"),
                            ("waiting", "waiting"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("review_status_date", models.DateTimeField(blank=True, null=True)),
                ("started_date", models.DateTimeField(blank=True, null=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="VideoInterviewSubmission",
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
                ("submitted_date", models.DateTimeField(blank=True, null=True)),
                (
                    "review_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("approved", "approved"),
                            ("rejected", "rejected"),
                            ("waiting", "waiting"),
                        ],
                        max_length=20,
                        null=True,
                    ),
                ),
                ("review_status_date", models.DateTimeField(blank=True, null=True)),
                (
                    "video_file",
                    models.FileField(
                        blank=True, null=True, upload_to=_get_video_file_path
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="BootcampRunApplicationStep",
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
                ("due_date", models.DateTimeField(blank=True, null=True)),
                (
                    "application_step",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="run_steps",
                        to="applications.ApplicationStep",
                    ),
                ),
                (
                    "bootcamp_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="application_steps",
                        to="klasses.Klass",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BootcampApplication",
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
                (
                    "resume_file",
                    models.FileField(
                        null=True, upload_to=applications.models._get_resume_upload_path
                    ),
                ),
                (
                    "state",
                    django_fsm.FSMField(
                        choices=[
                            (
                                "AWAITING_PROFILE_COMPLETION",
                                "AWAITING_PROFILE_COMPLETION",
                            ),
                            ("AWAITING_RESUME", "AWAITING_RESUME"),
                            ("AWAITING_USER_SUBMISSIONS", "AWAITING_USER_SUBMISSIONS"),
                            (
                                "AWAITING_SUBMISSION_REVIEW",
                                "AWAITING_SUBMISSION_REVIEW",
                            ),
                            ("AWAITING_PAYMENT", "AWAITING_PAYMENT"),
                            ("COMPLETE", "COMPLETE"),
                            ("REJECTED", "REJECTED"),
                        ],
                        default="AWAITING_PROFILE_COMPLETION",
                        max_length=50,
                    ),
                ),
                (
                    "bootcamp_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="klasses.Klass",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="ecommerce.Order",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bootcamp_applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ApplicationStepSubmission",
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
                ("object_id", models.PositiveIntegerField()),
                (
                    "bootcamp_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="applications.BootcampApplication",
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        help_text="The type of submission",
                        limit_choices_to=models.Q(
                            models.Q(
                                ("app_label", "applications"),
                                ("model", "videointerviewsubmission"),
                            ),
                            models.Q(
                                ("app_label", "applications"),
                                ("model", "quizsubmission"),
                            ),
                            _connector="OR",
                        ),
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
                (
                    "run_application_step",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="applications.BootcampRunApplicationStep",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
    ]
