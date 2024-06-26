"""Models for bootcamp applications"""

from decimal import Decimal
from uuid import uuid4
from functools import reduce
from operator import or_

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.urls import reverse
from django_fsm import FSMField, transition, RETURN_VALUE
from wagtail.fields import RichTextField
from mitol.common.utils import now_in_utc
from mitol.common.models import TimestampedModel

from applications.constants import (
    VALID_SUBMISSION_TYPE_CHOICES,
    AppStates,
    VALID_APP_STATE_CHOICES,
    VALID_REVIEW_STATUS_CHOICES,
    VALID_SUBMISSION_STATUS_CHOICES,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    SUBMISSION_STATUS_PENDING,
    LETTER_TYPE_APPROVED,
    LETTER_TYPE_REJECTED,
    VALID_LETTER_TYPE_CHOICES,
)
from applications.constants import INTEGRATION_PREFIX
from applications.utils import validate_file_extension, check_eligibility_to_skip_steps
from ecommerce.models import Order
from jobma.models import Interview
from klasses.api import deactivate_run_enrollment, create_run_enrollment
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from main.models import ValidateOnSaveMixin


class ApplicationStep(models.Model):
    """Defines a stage in a bootcamp application for which users must submit/upload something"""

    bootcamp = models.ForeignKey(
        "klasses.Bootcamp", on_delete=models.CASCADE, related_name="application_steps"
    )
    step_order = models.PositiveSmallIntegerField(default=1)
    submission_type = models.CharField(
        choices=VALID_SUBMISSION_TYPE_CHOICES, max_length=40
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
        ApplicationStep, on_delete=models.CASCADE, related_name="run_steps"
    )
    bootcamp_run = models.ForeignKey(
        "klasses.BootcampRun",
        on_delete=models.CASCADE,
        related_name="application_steps",
    )
    due_date = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.bootcamp_run.bootcamp_id != self.application_step.bootcamp_id:
            raise ValidationError(
                "The bootcamp run does not match the bootcamp linked to the application step ({}, {}).".format(
                    self.bootcamp_run.bootcamp_id, self.application_step.bootcamp_id
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
        """
        Prefetches models that inform the state of bootcamp applications,
        and filters to only include fulfilled orders.
        """
        return self.select_related("user__profile", "bootcamp_run").prefetch_related(
            "submissions",
            models.Prefetch(
                "orders",
                queryset=Order.objects.filter(status=Order.FULFILLED).select_related(
                    "user__profile"
                ),
            ),
            "bootcamp_run__application_steps__application_step",
            "bootcamp_run__installment_set",
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
        User, on_delete=models.CASCADE, related_name="bootcamp_applications"
    )
    bootcamp_run = models.ForeignKey(
        "klasses.BootcampRun", on_delete=models.CASCADE, related_name="applications"
    )
    resume_file = models.FileField(
        upload_to=_get_resume_upload_path, null=True, blank=True
    )
    linkedin_url = models.URLField(blank=True, null=True)
    resume_upload_date = models.DateTimeField(null=True, blank=True)
    state = FSMField(
        default=AppStates.AWAITING_PROFILE_COMPLETION.value,
        choices=VALID_APP_STATE_CHOICES,
    )

    @property
    def total_paid(self):
        """Calculate the total paid of all fulfilled orders for this application"""
        return sum(
            order.total_price_paid
            for order in self.orders.all()
            if order.status == Order.FULFILLED
        )

    @property
    def price(self):
        """Calculate the price for the user, possibly their personal price or else the full price"""
        bootcamp_run = self.bootcamp_run
        return bootcamp_run.personal_price(self.user) or Decimal(0)

    @property
    def is_paid_in_full(self):
        """Calculate if the user has fully paid for their application"""
        return self.total_paid >= self.price

    @transition(
        field=state,
        source=[
            AppStates.AWAITING_RESUME.value,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ],
        target=RETURN_VALUE(
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
            AppStates.AWAITING_PAYMENT.value,
        ),
    )
    def add_resume(self, *, resume_file=None, linkedin_url=None):
        """Add resume and/or linkedin URL to the application and transition to a new state"""
        if resume_file:
            validate_file_extension(resume_file)
            self.resume_file = resume_file
        if linkedin_url:
            self.linkedin_url = linkedin_url
        self.resume_upload_date = now_in_utc()
        self.save()

        if self.state == AppStates.AWAITING_RESUME.value:
            application_steps = BootcampRunApplicationStep.objects.filter(
                bootcamp_run=self.bootcamp_run
            )
            if application_steps.exists():
                return AppStates.AWAITING_USER_SUBMISSIONS.value
            else:
                return AppStates.AWAITING_PAYMENT.value
        return self.state

    @transition(
        field=state,
        source=AppStates.AWAITING_SUBMISSION_REVIEW.value,
        target=RETURN_VALUE(
            AppStates.AWAITING_USER_SUBMISSIONS.value, AppStates.AWAITING_PAYMENT.value
        ),
    )
    def approve_submission(self):
        """Approve application submission"""
        from applications.tasks import create_and_send_applicant_letter

        if self.is_ready_for_payment():
            create_and_send_applicant_letter.delay(
                application_id=self.id, letter_type=LETTER_TYPE_APPROVED
            )
            return AppStates.AWAITING_PAYMENT.value
        else:
            return AppStates.AWAITING_USER_SUBMISSIONS.value

    @transition(
        field=state,
        source=AppStates.AWAITING_USER_SUBMISSIONS.value,
        target=AppStates.AWAITING_SUBMISSION_REVIEW.value,
    )
    def complete_submission(self):
        """When the submission is completed, mark that it is ready for review"""

    @transition(
        field=state,
        source=AppStates.AWAITING_SUBMISSION_REVIEW.value,
        target=AppStates.REJECTED.value,
    )
    def reject_submission(self):
        """Reject application submission"""
        from applications.tasks import create_and_send_applicant_letter

        create_and_send_applicant_letter.delay(
            application_id=self.id, letter_type=LETTER_TYPE_REJECTED
        )

    @transition(
        field=state,
        source=[
            AppStates.REJECTED.value,
            AppStates.AWAITING_PAYMENT.value,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
        ],
        target=AppStates.AWAITING_SUBMISSION_REVIEW.value,
    )
    def revert_decision(self):
        """Revert previous submission decision"""

    @transition(
        field=state,
        source=AppStates.AWAITING_PAYMENT.value,
        target=AppStates.COMPLETE.value,
    )
    def complete(self):
        """Mark the application as completed"""
        create_run_enrollment(self.user, self.bootcamp_run)

    @transition(
        field=state,
        source=AppStates.COMPLETE.value,
        target=AppStates.AWAITING_PAYMENT.value,
    )
    def await_further_payment(self):
        """Mark the application as awaiting payment after a price change"""
        deactivate_run_enrollment(
            user=self.user, bootcamp_run=self.bootcamp_run, change_status=None
        )

    @transition(
        field=state,
        source=[
            AppStates.COMPLETE.value,
            AppStates.AWAITING_PAYMENT.value,
            AppStates.REFUNDED.value,
        ],
        target=AppStates.REFUNDED.value,
    )
    def refund(self):
        """Mark the application as refunded"""
        deactivate_run_enrollment(
            user=self.user,
            bootcamp_run=self.bootcamp_run,
            change_status=ENROLL_CHANGE_STATUS_REFUNDED,
        )

    @transition(
        field=state,
        source=[
            AppStates.AWAITING_PROFILE_COMPLETION.value,
            AppStates.AWAITING_RESUME.value,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ],
        target=AppStates.AWAITING_PAYMENT.value,
        conditions=[check_eligibility_to_skip_steps],
    )
    def skip_application_steps(self):
        """skip application steps for alumni"""

    def all_application_steps_submitted(self):
        """
        Check if the user has submissions for all application steps.
        """
        return self.submissions.count() == self.bootcamp_run.application_steps.count()

    def is_ready_for_payment(self):
        """
        Make sure all steps are submitted, reviewed and approved
        """
        if self.all_application_steps_submitted():
            return not self.submissions.exclude(
                review_status=REVIEW_STATUS_APPROVED
            ).exists()
        return False

    @property
    def integration_id(self):
        """
        Return an integration id to be used by Hubspot as the unique deal id.
        This is necessary because the integration id used to be based on PersonalPrice.id,
        and going forward, not all applicants will have a PersonalPrice.  So hubspot deals
        will be based on BootcampApplication instead and this requires that there be no
        overlap in integration ids between new and old deals.

        Returns:
            str: the integration id
        """
        return f"{INTEGRATION_PREFIX}{self.id}"

    def __str__(self):
        return f"user='{self.user.email}', run='{self.bootcamp_run.title}', state={self.state}"


class BootcampApplicationLine(TimestampedModel):
    """Dummy class for maintaining hubspot ids for deal (aka BootcampApplication) line_items"""

    application = models.OneToOneField(
        BootcampApplication,
        unique=True,
        null=True,
        related_name="line",
        on_delete=models.CASCADE,
    )


class SubmissionTypeModel(TimestampedModel):
    """Base model for any type of submission that is required on a user's bootcamp application"""

    submission_step_title = None

    class Meta:
        abstract = True


class VideoInterviewSubmission(SubmissionTypeModel):
    """A video interview that was submitted for review in a bootcamp application"""

    submission_step_title = "Video Interview"
    app_step_submissions = GenericRelation(
        "applications.ApplicationStepSubmission", related_query_name="videointerviews"
    )
    interview = models.OneToOneField(Interview, on_delete=models.CASCADE)


class QuizSubmission(SubmissionTypeModel):
    """A quiz that was submitted for review in a bootcamp application"""

    submission_step_title = "Quiz"
    app_step_submissions = GenericRelation(
        "applications.ApplicationStepSubmission", related_query_name="quizzes"
    )

    started_date = models.DateTimeField(null=True, blank=True)


APP_SUBMISSION_MODELS = [VideoInterviewSubmission, QuizSubmission]


class ApplicationStepSubmission(TimestampedModel, ValidateOnSaveMixin):
    """An item that was uploaded/submitted for review by a user as part of their bootcamp application"""

    bootcamp_application = models.ForeignKey(
        BootcampApplication, on_delete=models.CASCADE, related_name="submissions"
    )
    run_application_step = models.ForeignKey(
        BootcampRunApplicationStep, on_delete=models.CASCADE, related_name="submissions"
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    review_status = models.CharField(
        max_length=20,
        choices=VALID_REVIEW_STATUS_CHOICES,
        default=REVIEW_STATUS_PENDING,
    )
    submission_status = models.CharField(
        max_length=20,
        choices=VALID_SUBMISSION_STATUS_CHOICES,
        default=SUBMISSION_STATUS_PENDING,
    )
    review_status_date = models.DateTimeField(null=True, blank=True)
    # This limits the choice of content type to models we have specified as application submission models
    valid_submission_types = reduce(
        or_,
        (
            models.Q(app_label="applications", model=model_cls._meta.model_name)
            for model_cls in APP_SUBMISSION_MODELS
        ),  # pylint: disable=protected-access
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
        if (
            self.bootcamp_application.bootcamp_run
            != self.run_application_step.bootcamp_run
        ):
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


class ApplicantLetter(TimestampedModel):
    """Represents a letter sent to an applicant, with a hash so the user can view the letter afterwards"""

    letter_type = models.CharField(choices=VALID_LETTER_TYPE_CHOICES, max_length=255)
    letter_subject = models.TextField()
    letter_text = RichTextField()
    application = models.ForeignKey(BootcampApplication, on_delete=models.CASCADE)
    hash = models.UUIDField(unique=True, default=uuid4)

    def get_absolute_url(self):
        """Return the absolute URL for use with Django Admin"""
        return reverse("letters", kwargs={"hash": self.hash})

    def __str__(self):
        return f"Letter for {self.application}, type={self.letter_type}"
