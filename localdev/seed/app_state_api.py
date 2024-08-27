"""API functionality for setting the state of an application"""

import os
import random

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db.models import Max
from mitol.common.utils import now_in_utc

from applications.constants import (
    ORDERED_UNFINISHED_APP_STATES,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_REJECTED,
    SUBMISSION_QUIZ,
    SUBMISSION_REVIEW_COMPLETED_STATES,
    SUBMISSION_STATUS_SUBMITTED,
    SUBMISSION_VIDEO,
    AppStates,
)
from applications.models import (
    ApplicationStepSubmission,
    QuizSubmission,
    VideoInterviewSubmission,
)
from ecommerce.api import complete_successful_order
from ecommerce.models import Line, Order
from jobma.constants import COMPLETED
from jobma.models import Interview, Job
from main.utils import get_filename_from_path, partition_around_index
from profiles.api import is_user_info_complete
from profiles.models import LegalAddress, Profile

User = get_user_model()

ALLOWED_STATES = ORDERED_UNFINISHED_APP_STATES + [AppStates.COMPLETE.value]  # noqa: RUF005
DUMMY_RESUME_FILEPATH = "localdev/seed/resources/dummy_resume.pdf"
DUMMY_RESUME_FILENAME = get_filename_from_path(DUMMY_RESUME_FILEPATH)
DUMMY_RESUME_ENCODING = "iso-8859-1"
DUMMY_LINKEDIN_URL = "http://example.com/linkedin"
DUMMY_INTERVIEW_URL = ("http://example.com/video",)
DUMMY_INTERVIEW_RESULTS_URL = "http://example.com/video-result"
INTERVIEW_TEMPLATE_ID = 123

PROFILE_CHOICES = {
    "company": ("MIT", "Boeing"),
    "gender": ("m", "f", "o"),
    "birth_year": (1950, 1960, 1970, 1980, 1990),
    "job_title": ("Software Developer", "Administrator", "Professor", "Emperor"),
    "industry": ("Tech", "Higher Ed"),
    "job_function": ("Working hard", "Hardly working"),
    "company_size": (9, 99),
    "years_experience": (2, 5, 10),
    "highest_education": ("Doctorate", "Bachelor's degree"),
    "name": (
        "Joseph M. Acaba",
        "Kayla Barron",
        "Raja Chari",
        "Jeanatte J. Epps",
        "Bob Hines",
        "Jonny Kim",
        "Nicole Aunapu Mann",
        "Kathleen Rubins",
        "Mark T. Vande Hei",
    ),
}
LEGAL_ADDRESS_CHOICES = {
    "street_address_1": ("1 Main St", "500 Technology Square", "4 Washington Lane"),
    "city": ("Cambridge", "Boston", "Somerville", "Townsville"),
    "country": ("US",),
    "state_or_territory": ("US-MA", "US-CT", "US-VT", "US-NH"),
    "postal_code": ("02139", "02201", "02139"),
}


def fill_out_registration_info(user):
    """Ensures that the user has a fully filled out profile and legal address"""
    profile, profile_created = Profile.objects.get_or_create(user=user)
    if profile_created or not profile.is_complete:
        profile.name = random.choice(PROFILE_CHOICES["name"])
        profile_field_values = [
            (field_name, values)
            for field_name, values in PROFILE_CHOICES.items()
            if field_name != "name"
        ]
        for field_name, values in profile_field_values:
            setattr(profile, field_name, random.choice(values))
        profile.save()
    if not profile.name:
        profile.name = random.choice(PROFILE_CHOICES["name"])
        profile.save()
    if not hasattr(user, "legal_address"):
        legal_address_props = {
            prop_name: random.choice(prop_values)
            for prop_name, prop_values in LEGAL_ADDRESS_CHOICES.items()
        }
        legal_address = LegalAddress.objects.create(
            user=user,
            first_name=profile.name.split(" ")[0],
            last_name=" ".join(profile.name.split(" ")[1:]),
            **legal_address_props,
        )
    else:
        legal_address = user.legal_address
    return user, profile, legal_address


def fulfill_video_interview(application, run_application_step):
    """
    Ensures that a user has a completed video interview submission for the given application and step

    Args:
        application (applications.models.BootcampApplication):
        run_application_step (applications.models.BootcampRunApplicationStep):

    Returns:
        ApplicationStepSubmission: The created or updated submission
    """
    # If Job records already exist, use the max job_id value and add 1 for the new job_id. Otherwise use 1.
    job_id = (
        1
        if Job.objects.count() == 0
        else (Job.objects.aggregate(max_job_id=Max("job_id"))["max_job_id"] + 1)
    )
    job, _ = Job.objects.get_or_create(
        run=application.bootcamp_run,
        defaults=dict(  # noqa: C408
            job_title=application.bootcamp_run.title,
            job_id=job_id,
            job_code=f"job_run_{application.bootcamp_run.id}",
            interview_template_id=INTERVIEW_TEMPLATE_ID,
        ),
    )
    interview, _ = Interview.objects.get_or_create(
        job=job,
        applicant=application.user,
        defaults=dict(  # noqa: C408
            status=COMPLETED,
            interview_url=DUMMY_INTERVIEW_URL,
            results_url=DUMMY_INTERVIEW_RESULTS_URL,
            interview_token="".join([str(random.randint(0, 9)) for _ in range(9)]),
        ),
    )
    submission, _ = VideoInterviewSubmission.objects.get_or_create(interview=interview)
    step_submission, _ = ApplicationStepSubmission.objects.update_or_create(
        bootcamp_application=application,
        run_application_step=run_application_step,
        defaults=dict(  # noqa: C408
            submitted_date=now_in_utc(),
            review_status=REVIEW_STATUS_PENDING,
            review_status_date=None,
            submission_status=SUBMISSION_STATUS_SUBMITTED,
            content_type=ContentType.objects.get(
                app_label="applications", model=SUBMISSION_VIDEO
            ),
            object_id=submission.id,
        ),
    )
    return step_submission


def fulfill_quiz_interview(application, run_application_step):
    """
    Ensures that a user has a completed quiz interview submission for the given application and step

    Args:
        application (applications.models.BootcampApplication):
        run_application_step (applications.models.BootcampRunApplicationStep):

    Returns:
        ApplicationStepSubmission: The created or updated submission
    """
    submission = QuizSubmission.objects.create(started_date=None)
    step_submission, _ = ApplicationStepSubmission.objects.update_or_create(
        bootcamp_application=application,
        run_application_step=run_application_step,
        defaults=dict(  # noqa: C408
            submitted_date=now_in_utc(),
            review_status=REVIEW_STATUS_PENDING,
            review_status_date=None,
            submission_status=SUBMISSION_STATUS_SUBMITTED,
            content_type=ContentType.objects.get(
                app_label="applications", model=SUBMISSION_QUIZ
            ),
            object_id=submission.id,
        ),
    )
    return step_submission


SUBMISSION_FACTORIES = {
    SUBMISSION_VIDEO: fulfill_video_interview,
    SUBMISSION_QUIZ: fulfill_quiz_interview,
}


class AppStep:
    """Base class for evaluating/setting an application at a certain state"""

    state = None

    @staticmethod
    def is_fulfilled(application):
        """Returns True if the given application step has been fulfilled"""
        raise NotImplementedError

    @staticmethod
    def _fulfill(application, **kwargs):
        """Performs the necessary data manipulation to fulfill this step of the application"""
        raise NotImplementedError

    @staticmethod
    def _revert(application):
        """
        Performs the necessary data manipulation to ensure that this step of the application has not been fulfilled
        """
        raise NotImplementedError

    @classmethod
    def fulfill(cls, application, **kwargs):
        """
        Performs the necessary data manipulation to fulfill this step of the application, and ensures that the
        application is in the correct state afterwards
        """
        cls._fulfill(application, **kwargs)
        # NOTE: These functions perform some data manipulation on an application that aren't supported by normal
        # functionality, hence the manual setting of the state instead of using state transitions.
        application.refresh_from_db()
        state_idx = ORDERED_UNFINISHED_APP_STATES.index(cls.state)
        new_state = (
            AppStates.COMPLETE.value
            if state_idx == len(ORDERED_UNFINISHED_APP_STATES) - 1
            else ORDERED_UNFINISHED_APP_STATES[state_idx + 1]
        )
        application.state = new_state
        application.save()

    @classmethod
    def revert(cls, application):
        """
        Performs the necessary data manipulation to ensure that this step of the application has not been fulfilled,
        and ensures that the application is in the correct state afterwards
        """
        cls._revert(application)
        # NOTE: These functions perform some data manipulation on an application that aren't supported by normal
        # functionality, hence the manual setting of the state instead of using state transitions.
        application.refresh_from_db()
        application.state = cls.state
        application.save()


class AwaitingProfileStep(AppStep):
    """Provides functionality for fulfilling or reverting the 'awaiting profile' step of an application"""

    state = AppStates.AWAITING_PROFILE_COMPLETION.value

    @staticmethod
    def is_fulfilled(application):  # noqa: D102
        return is_user_info_complete(application.user)

    @staticmethod
    def _fulfill(application, **kwargs):  # noqa: ARG004
        fill_out_registration_info(application.user)

    @staticmethod
    def _revert(application):
        LegalAddress.objects.filter(user=application.user).delete()


class AwaitingResumeStep(AppStep):
    """Provides functionality for fulfilling or reverting the 'awaiting resume' step of an application"""

    state = AppStates.AWAITING_RESUME.value

    @staticmethod
    def is_fulfilled(application):  # noqa: D102
        return application.resume_upload_date is not None and (
            application.resume_file is not None or application.linkedin_url is not None
        )

    @staticmethod
    def _fulfill(application, **kwargs):  # noqa: ARG004
        with open(  # noqa: PTH123
            os.path.join(settings.BASE_DIR, DUMMY_RESUME_FILEPATH),
            "rb",  # noqa: PTH118
        ) as resume_file:
            application.add_resume(
                resume_file=File(resume_file, name=DUMMY_RESUME_FILENAME),
                linkedin_url=DUMMY_LINKEDIN_URL,
            )
        application.save()

    @staticmethod
    def _revert(application):
        if application.resume_file is not None:
            application.resume_file.delete()
        application.resume_file = None
        application.linkedin_url = None
        application.resume_upload_date = None
        application.save()


class AwaitingSubmissionsStep(AppStep):
    """Provides functionality for fulfilling or reverting the 'awaiting submissions' step of an application"""

    state = AppStates.AWAITING_USER_SUBMISSIONS.value

    @staticmethod
    def is_fulfilled(application):  # noqa: D102
        submissions = list(application.submissions.all())
        submission_review_statuses = [
            submission.review_status for submission in submissions
        ]
        if any(  # noqa: RET503, SIM114
            [status == REVIEW_STATUS_REJECTED for status in submission_review_statuses]  # noqa: C419
        ):
            return True
        elif any(
            [status == REVIEW_STATUS_PENDING for status in submission_review_statuses]  # noqa: C419
        ):
            return True
        elif len(submissions) < application.bootcamp_run.application_steps.count():
            return False

    @staticmethod
    def _fulfill(application, **kwargs):
        num_to_fulfill = kwargs.get("num_submissions", None)
        run_steps = application.bootcamp_run.application_steps.order_by(
            "application_step__step_order"
        ).all()
        num_to_fulfill = num_to_fulfill or len(run_steps)
        if num_to_fulfill and num_to_fulfill > len(run_steps):
            raise ValidationError(
                "{} step(s) exist. Cannot fulfill {}.".format(  # noqa: EM103
                    len(run_steps), num_to_fulfill
                )
            )
        for i, run_step in enumerate(run_steps):
            if i >= num_to_fulfill:
                break
            submission_factory = SUBMISSION_FACTORIES[
                run_step.application_step.submission_type
            ]
            submission_factory(application, run_step)

    @staticmethod
    def _revert(application):
        application.submissions.all().delete()


class AwaitingReviewStep(AppStep):
    """Provides functionality for fulfilling or reverting the 'awaiting submission review' step of an application"""

    state = AppStates.AWAITING_SUBMISSION_REVIEW.value

    @staticmethod
    def is_fulfilled(application):  # noqa: D102
        submissions = list(application.submissions.all())
        submission_review_statuses = [
            submission.review_status for submission in submissions
        ]
        return len(submissions) > 0 and len(submissions) == len(
            [
                status
                for status in submission_review_statuses
                if status in SUBMISSION_REVIEW_COMPLETED_STATES
            ]
        )

    @staticmethod
    def _fulfill(application, **kwargs):
        num_to_fulfill = kwargs.get("num_reviews", None)
        submissions = list(
            application.submissions.order_by(
                "run_application_step__application_step__step_order"
            ).all()
        )
        num_to_fulfill = num_to_fulfill or len(submissions)
        if num_to_fulfill and num_to_fulfill > len(submissions):
            raise ValidationError(
                "{} submission(s) exist. Cannot fulfill {}.".format(  # noqa: EM103
                    len(submissions), num_to_fulfill
                )
            )
        now = now_in_utc()
        for i, submission in enumerate(submissions):
            if i >= num_to_fulfill:
                break
            submission.review_status = REVIEW_STATUS_APPROVED
            submission.review_status_date = now
            submission.save()

    @staticmethod
    def _revert(application):
        application.submissions.update(
            review_status=REVIEW_STATUS_PENDING, review_status_date=None
        )


class AwaitingPaymentStep(AppStep):
    """Provides functionality for fulfilling or reverting the 'awaiting payment' step of an application"""

    state = AppStates.AWAITING_PAYMENT.value

    @staticmethod
    def is_fulfilled(application):  # noqa: D102
        return application.is_paid_in_full

    @staticmethod
    def _fulfill(application, **kwargs):  # noqa: ARG004
        run = application.bootcamp_run
        total_run_price = run.price
        order, _ = Order.objects.update_or_create(
            user=application.user,
            application=application,
            defaults=dict(status=Order.FULFILLED, total_price_paid=total_run_price),  # noqa: C408
        )
        Line.objects.update_or_create(
            order=order,
            bootcamp_run=run,
            defaults=dict(price=total_run_price),  # noqa: C408
        )
        complete_successful_order(order, send_receipt=False)

    @staticmethod
    def _revert(application):
        Order.objects.filter(application=application).delete()


ORDERED_APPLICATION_STEP_CLASSES = [
    AwaitingProfileStep,
    AwaitingResumeStep,
    AwaitingSubmissionsStep,
    AwaitingReviewStep,
    AwaitingPaymentStep,
]


def set_application_state(application, target_state):
    """
    Manipulates the given application into the target state.

    Args:
        application (BootcampApplication):
        target_state (str): The desired state of the application

    Returns:
        BootcampApplication: The updated application
    """
    if settings.ENVIRONMENT in {"prod", "production"}:
        raise ValidationError("This API function cannot be used in production")  # noqa: EM101
    assert target_state in ALLOWED_STATES
    if target_state == AppStates.COMPLETE.value:
        previous_step_classes, next_step_classes = (
            ORDERED_APPLICATION_STEP_CLASSES,
            [],
        )
        target_step_cls = None
    else:
        target_state_cls_index = next(
            i
            for i, step_cls in enumerate(ORDERED_APPLICATION_STEP_CLASSES)
            if step_cls.state == target_state
        )
        previous_step_classes, next_step_classes = partition_around_index(
            ORDERED_APPLICATION_STEP_CLASSES, target_state_cls_index
        )
        target_step_cls = ORDERED_APPLICATION_STEP_CLASSES[target_state_cls_index]
    # Revert all steps that come after the target
    for step_cls in reversed(next_step_classes):
        step_cls.revert(application)
    # Apply/fulfill all steps before the target (if not already fulfilled)
    for step_cls in previous_step_classes:
        if not step_cls.is_fulfilled(application):
            step_cls.fulfill(application)
    if target_step_cls:
        # Make sure that the target state hasn't already been fulfilled
        target_step_cls.revert(application)
    return application
