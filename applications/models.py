"""Models for bootcamp applications"""
from uuid import uuid4
from functools import reduce
from operator import or_
import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django_fsm import FSMField, transition

from applications.constants import (
    SubmissionTypes,
    VALID_SUBMISSION_TYPE_CHOICES,
    AppStates,
    VALID_APP_STATE_CHOICES,
    VALID_REVIEW_STATUS_CHOICES
)
from applications.utils import validate_file_extension
from main.models import TimestampedModel, ValidateOnSaveMixin


class ApplicationStep(models.Model):
    """Defines a stage in a bootcamp application for which users must submit/upload something"""
    bootcamp = models.ForeignKey(
        'klasses.Bootcamp',
        on_delete=models.CASCADE,
        related_name='application_steps'
    )
    step_order = models.PositiveSmallIntegerField(default=1)
    submission_type = models.CharField(
        choices=VALID_SUBMISSION_TYPE_CHOICES, max_length=30
    )

    class Meta:
        unique_together = ["bootcamp", "step_order"]
        ordering = ["bootcamp", "step_order"]

    def __str__(self):
        return f"bootcamp='{self.bootcamp.title}', step={self.step_order}, type={self.submission_type}"


class BootcampRunApplicationStep(ValidateOnSaveMixin):
    """
    Defines a due date and other metadata for a bootcamp application step as it applies to a specific run
    of that bootcamp
    """
    application_step = models.ForeignKey(
        ApplicationStep,
        on_delete=models.CASCADE,
        related_name='run_steps'
    )
    bootcamp_run = models.ForeignKey(
        'klasses.BootcampRun',
        on_delete=models.CASCADE,
        related_name='application_steps'
    )
    due_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.bootcamp_run.bootcamp_id != self.application_step.bootcamp_id:
            raise ValidationError(
                "The bootcamp run does not match the bootcamp linked to the application step ({}, {}).".format(
                    self.bootcamp_run.bootcamp_id,
                    self.application_step.bootcamp_id,
                )
            )
        return super().clean()

    def __str__(self):
        return (
            f"run='{self.bootcamp_run.title}', step={self.application_step.step_order}, "
            f"due={None if self.due_date is None else self.due_date.strftime('%m/%d/%Y')}"
        )


def _get_resume_upload_path(instance, filename):
    """
    Produces the file path for an uploaded resume

    Return:
         str: The file path
    """
    return f"resumes/{instance.user.id}/{uuid4()}_{filename}"


class BootcampApplicationQuerySet(models.QuerySet):
    """Custom queryset for BootcampApplication model"""
    def prefetch_state_data(self):
        """Prefetches models that inform the state of bootcamp applications"""
        return (
            self.select_related(
                "user__profile", "order"
            ).prefetch_related(
                "submissions", "application_steps"
            )
        )


class BootcampApplicationManager(models.Manager):
    """Custom manager for BootcampApplication model"""
    def get_queryset(self):  # pylint:disable=missing-docstring
        return BootcampApplicationQuerySet(self.model, using=self._db)

    def prefetch_state_data(self):
        """Prefetches models that inform the state of bootcamp applications"""
        return self.get_queryset().prefetch_state_data()


class BootcampApplication(TimestampedModel):
    """A user's application to a run of a bootcamp"""
    objects = BootcampApplicationManager()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bootcamp_applications'
    )
    bootcamp_run = models.ForeignKey(
        'klasses.BootcampRun',
        on_delete=models.CASCADE,
        related_name='applications'
    )
    resume_file = models.FileField(upload_to=_get_resume_upload_path, null=True, blank=True)
    resume_upload_date = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(
        'ecommerce.Order',
        on_delete=models.CASCADE,
        related_name='applications',
        null=True,
        blank=True
    )
    state = FSMField(default=AppStates.AWAITING_PROFILE_COMPLETION.value, choices=VALID_APP_STATE_CHOICES)

    @transition(
        field=state,
        source=[AppStates.AWAITING_RESUME, AppStates.AWAITING_USER_SUBMISSIONS],
        target=AppStates.AWAITING_USER_SUBMISSIONS
    )
    def upload_resume(self, resume_file):
        """Save resume and make sure that the state can be transitioned to a new state"""
        validate_file_extension(resume_file)
        self.resume_file = resume_file
        self.resume_upload_date = datetime.datetime.now()
        self.save()

    def __str__(self):
        return f"user='{self.user.email}', run='{self.bootcamp_run.title}', state={self.state}"


class SubmissionTypeModel(TimestampedModel):
    """Base model for any type of submission that is required on a user's bootcamp application"""
    submission_type = None

    class Meta:
        abstract = True


def _get_video_file_path(instance, filename):  # pylint: disable=unused-argument
    """
    Produces the file path for an uploaded video interview

    Return:
         str: The file path
    """
    return f"video_interviews/{uuid4()}_{filename}"


class VideoInterviewSubmission(SubmissionTypeModel):
    """A video interview that was submitted for review in a bootcamp application"""
    submission_type = SubmissionTypes.VIDEO_INTERVIEW.value
    app_step_submissions = GenericRelation(
        "applications.ApplicationStepSubmission",
        related_query_name="videointerviews"
    )

    video_file = models.FileField(upload_to=_get_video_file_path, null=True, blank=True)


class QuizSubmission(SubmissionTypeModel):
    """A quiz that was submitted for review in a bootcamp application"""
    submission_type = SubmissionTypes.QUIZ.value
    app_step_submissions = GenericRelation(
        "applications.ApplicationStepSubmission",
        related_query_name="quizzes"
    )

    started_date = models.DateTimeField(null=True, blank=True)


APP_SUBMISSION_MODELS = [VideoInterviewSubmission, QuizSubmission]


class ApplicationStepSubmission(TimestampedModel, ValidateOnSaveMixin):
    """An item that was uploaded/submitted for review by a user as part of their bootcamp application"""
    bootcamp_application = models.ForeignKey(
        BootcampApplication,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    run_application_step = models.ForeignKey(
        BootcampRunApplicationStep,
        on_delete=models.CASCADE,
        related_name='submissions'
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=VALID_REVIEW_STATUS_CHOICES, null=True, blank=True)
    review_status_date = models.DateTimeField(null=True, blank=True)
    # This limits the choice of content type to models we have specified as application submission models
    valid_submission_types = reduce(
        or_,
        (
            models.Q(app_label="applications", model=model_cls._meta.model_name)
            for model_cls in APP_SUBMISSION_MODELS
        )  # pylint: disable=protected-access
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=valid_submission_types,
        help_text="The type of submission",
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        # Users should not be able to provide multiple submissions for the same application step
        unique_together = ["bootcamp_application", "run_application_step"]

    def clean(self):
        if self.bootcamp_application.bootcamp_run != self.run_application_step.bootcamp_run:
            raise ValidationError(
                "The application step does not match the application's bootcamp run ({}, {}).".format(
                    self.bootcamp_application.bootcamp_run_id,
                    self.run_application_step.bootcamp_run_id,
                )
            )
        return super().clean()

    def __str__(self):
        return (
            f"user='{self.bootcamp_application.user.email}', run='{self.bootcamp_application.bootcamp_run.title}', "
            f"contenttype={self.content_type}, object={self.object_id}"
        )
