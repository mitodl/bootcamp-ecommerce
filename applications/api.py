"""API for bootcamp applications app"""
from django.db import transaction

from applications.constants import (
    AppStates,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_APPROVED,
)
from applications.exceptions import InvalidApplicationException
from applications.models import BootcampApplication
from main.utils import now_in_utc


@transaction.atomic
def get_or_create_bootcamp_application(user, bootcamp_run_id):
    """
    Fetches a bootcamp application for a user if it exists. Otherwise, an application is created with the correct
    state.

    Args:
        user (User): The user applying for the bootcamp run
        bootcamp_run_id (int): The id of the bootcamp run to which the user is applying

    Returns:
        Tuple[BootcampApplication, bool]: The bootcamp application paired with a boolean indicating whether
            or not a new application was created
    """
    bootcamp_app, created = BootcampApplication.objects.select_for_update().get_or_create(
        user=user, bootcamp_run_id=bootcamp_run_id
    )
    if created:
        derived_state = derive_application_state(bootcamp_app)
        bootcamp_app.state = derived_state
        bootcamp_app.save()
    return bootcamp_app, created


def derive_application_state(
    bootcamp_application
):  # pylint: disable=too-many-return-statements
    """
    Returns the correct state that an application should be in based on the application object itself and related data

    Args:
        bootcamp_application (BootcampApplication): A bootcamp application

    Returns:
        str: The derived state of the bootcamp application based on related data
    """
    if (
        not hasattr(bootcamp_application.user, "profile")
        or not bootcamp_application.user.profile.is_complete
    ):
        return AppStates.AWAITING_PROFILE_COMPLETION.value
    if not bootcamp_application.resume_file:
        return AppStates.AWAITING_RESUME.value
    submissions = list(bootcamp_application.submissions.all())
    submission_review_statuses = [
        submission.review_status for submission in submissions
    ]
    if any([status == REVIEW_STATUS_REJECTED for status in submission_review_statuses]):
        return AppStates.REJECTED.value
    elif any([status is None for status in submission_review_statuses]):
        return AppStates.AWAITING_SUBMISSION_REVIEW.value
    elif len(submissions) < bootcamp_application.bootcamp_run.application_steps.count():
        return AppStates.AWAITING_USER_SUBMISSIONS.value
    elif not bootcamp_application.is_paid_in_full:
        return AppStates.AWAITING_PAYMENT.value
    return AppStates.COMPLETE.value


def get_required_submission_type(application):
    """
    Get the submission type of the first unsubmitted step for an application

    Args:
        application (BootcampApplication): The application to query

    Returns:
        str: The submission type

    """
    submission_subquery = application.submissions.all()
    return (
        application.bootcamp_run.application_steps.exclude(
            id__in=submission_subquery.values_list("run_application_step", flat=True)
        )
        .order_by("application_step__step_order")
        .values_list("application_step__submission_type", flat=True)
        .first()
    )


def process_upload_resume(resume_file, linkedin_url, bootcamp_application):
    """
    Process the resume file and linkedin url and save it to BootcampApplication

    Args:
        resume_file (File): file profided by the user
        linkedin_url (str): a url provided by the user
        bootcamp_application (BootcampApplication): A bootcamp application

    """
    if bootcamp_application.state == AppStates.AWAITING_PROFILE_COMPLETION.value:
        raise InvalidApplicationException(
            "The BootcampApplication is still awaiting profile completion"
        )
    bootcamp_application.add_resume(resume_file=resume_file, linkedin_url=linkedin_url)
    # when state transition happens need to save manually
    bootcamp_application.save()


def set_submission_review_status(submission, review_status):
    """
    Process review of an application step submission

    Args:
        submission(ApplicationStepSubmission): The submission that is being reviewed
        review_status(str): approved or rejected submission
    """
    bootcamp_application = submission.bootcamp_application
    if bootcamp_application.state != AppStates.AWAITING_SUBMISSION_REVIEW.value:
        raise InvalidApplicationException(
            "The BootcampApplication is not awaiting submission review (id: {}, state: {})".format(
                bootcamp_application.id, bootcamp_application.state
            )
        )
    submission.review_status = review_status
    submission.review_status_date = now_in_utc()
    submission.save()
    if review_status == REVIEW_STATUS_APPROVED:
        bootcamp_application.approve_submission()
    else:
        bootcamp_application.reject_submission()
    bootcamp_application.save()
