"""API for bootcamp applications app"""
from django.db import transaction

from applications.constants import AppStates, REVIEW_STATUS_REJECTED
from applications.models import BootcampApplication
from ecommerce.models import Order


@transaction.atomic
def get_or_create_bootcamp_application(user, bootcamp_run):
    """
    Fetches a bootcamp application for a user if it exists. Otherwise, an application is created with the correct
    state.

    Args:
        user (User): The user applying for the bootcamp run
        bootcamp_run (klasses.models.BootcampRun): The bootcamp run to which the user is applying

    Returns:
        BootcampApplication: The bootcamp application
    """
    bootcamp_app, created = (
        BootcampApplication.objects
        .select_for_update()
        .get_or_create(
            user=user,
            bootcamp_run=bootcamp_run,
        )
    )
    if created:
        derived_state = derive_application_state(bootcamp_app)
        bootcamp_app.state = derived_state
        bootcamp_app.save()
    return bootcamp_app


def derive_application_state(bootcamp_application):  # pylint: disable=too-many-return-statements
    """
    Returns the correct state that an application should be in based on the application object itself and related data

    Args:
        bootcamp_application (BootcampApplication): A bootcamp application

    Returns:
        str: The derived state of the bootcamp application based on related data
    """
    if not hasattr(bootcamp_application.user, "profile") or not bootcamp_application.user.profile.is_complete:
        return AppStates.AWAITING_PROFILE_COMPLETION.value
    if not bootcamp_application.resume_file:
        return AppStates.AWAITING_RESUME.value
    submissions = list(bootcamp_application.submissions.all())
    submission_review_statuses = [submission.review_status for submission in submissions]
    if any([status == REVIEW_STATUS_REJECTED for status in submission_review_statuses]):
        return AppStates.REJECTED.value
    elif any([status is None for status in submission_review_statuses]):
        return AppStates.AWAITING_SUBMISSION_REVIEW.value
    elif len(submissions) < bootcamp_application.bootcamp_run.application_steps.count():
        return AppStates.AWAITING_USER_SUBMISSIONS.value
    if bootcamp_application.order is None or bootcamp_application.order.status != Order.FULFILLED:
        return AppStates.AWAITING_PAYMENT.value
    return AppStates.COMPLETE.value
