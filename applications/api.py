"""API for bootcamp applications app"""

import logging

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from applications import tasks
from applications.constants import (
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_REJECTED,
    SUBMISSION_VIDEO,
    AppStates,
)
from applications.models import (
    ApplicationStepSubmission,
    BootcampApplication,
    BootcampRunApplicationStep,
    VideoInterviewSubmission,
)
from applications.utils import check_eligibility_to_skip_steps
from jobma.api import create_interview_in_jobma
from jobma.models import Interview, Job
from profiles.api import is_user_info_complete

log = logging.getLogger()


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
    with transaction.atomic():
        (
            bootcamp_app,
            created,
        ) = BootcampApplication.objects.select_for_update().get_or_create(
            user=user, bootcamp_run_id=bootcamp_run_id
        )
        if created:
            derived_state = derive_application_state(bootcamp_app)
            bootcamp_app.state = derived_state
            bootcamp_app.save()

    if created:
        if check_eligibility_to_skip_steps(bootcamp_app):
            # for bootcamp with no application steps already in AWAITING_PAYMENT state
            if bootcamp_app.state != AppStates.AWAITING_PAYMENT.value:
                bootcamp_app.skip_application_steps()
                bootcamp_app.save()
        else:
            tasks.populate_interviews_in_jobma.delay(bootcamp_app.id)

    return bootcamp_app, created


def derive_application_state(  # noqa: PLR0911
    bootcamp_application,
):
    """
    Returns the correct state that an application should be in based on the application object itself and related data

    Args:
        bootcamp_application (BootcampApplication): A bootcamp application

    Returns:
        str: The derived state of the bootcamp application based on related data
    """
    if not is_user_info_complete(bootcamp_application.user):
        return AppStates.AWAITING_PROFILE_COMPLETION.value
    if bootcamp_application.bootcamp_run.application_steps.count() == 0:
        return AppStates.AWAITING_PAYMENT.value
    if not bootcamp_application.resume_file and not bootcamp_application.linkedin_url:
        return AppStates.AWAITING_RESUME.value
    submissions = list(bootcamp_application.submissions.all())
    submission_review_statuses = [
        submission.review_status for submission in submissions
    ]
    if any([status == REVIEW_STATUS_REJECTED for status in submission_review_statuses]):  # noqa: C419
        return AppStates.REJECTED.value
    elif any(
        [status == REVIEW_STATUS_PENDING for status in submission_review_statuses]  # noqa: C419
    ):
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


def refresh_jobma_interview_submissions(submissions):
    """
    Go over each ApplicationStep for the application and refresh the interview links from Jobma.

    Args:
        submissions (BootcampApplicationStep): A list of bootcamp application submissions
    """

    for submission in submissions:
        submission.content_object.interview.delete()
        populate_interviews_in_jobma(submission.bootcamp_application)
        log.debug(
            "Interview recreated for submission %d, application %d, user %s",
            submission.id,
            submission.bootcamp_application.id,
            submission.bootcamp_application.user.email,
        )


def populate_interviews_in_jobma(application):
    """
    Go over each ApplicationStep for the application and create the interviews in Jobma.

    Args:
        application (BootcampApplication): A bootcamp application
    """
    for run_step in BootcampRunApplicationStep.objects.filter(
        bootcamp_run=application.bootcamp_run,
        application_step__submission_type=SUBMISSION_VIDEO,
    ):
        # Job should be created by admin beforehand
        job = Job.objects.get(run=application.bootcamp_run)
        interview, _ = Interview.objects.get_or_create(
            applicant=application.user, job=job
        )
        if not interview.interview_url:
            create_interview_in_jobma(interview)

        # Make sure a VideoInterviewSubmission & ApplicationStepSubmission exist
        video_interview_submission, _ = VideoInterviewSubmission.objects.get_or_create(
            interview=interview
        )
        ApplicationStepSubmission.objects.get_or_create(
            bootcamp_application=application,
            run_application_step=run_step,
            defaults={
                "object_id": video_interview_submission.id,
                "content_type": ContentType.objects.get_for_model(
                    video_interview_submission
                ),
            },
        )
