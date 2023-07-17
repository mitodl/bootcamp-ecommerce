"""Tasks for applications"""
import logging
from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from mitol.common.utils import now_in_utc

from applications.constants import (
    SUBMISSION_STATUS_PENDING,
    REVIEW_COMPLETED_APP_STATES,
)
from applications.models import BootcampApplication, ApplicationStepSubmission
from applications import api
from main.celery import app

log = logging.getLogger()


@app.task
def create_and_send_applicant_letter(application_id, *, letter_type):
    """Create and send an applicant letter"""
    from applications import mail_api

    application = BootcampApplication.objects.get(id=application_id)
    mail_api.create_and_send_applicant_letter(application, letter_type=letter_type)


@app.task
def populate_interviews_in_jobma(application_id):
    """Create an interview in Jobma and update our models with a link to the Jobma interview"""
    application = BootcampApplication.objects.get(id=application_id)
    api.populate_interviews_in_jobma(application)


@app.task
def refresh_pending_interview_links():
    """Recreate old pending interviews"""
    now = now_in_utc()
    cutoff_date = now - timedelta(days=settings.JOBMA_LINK_EXPIRATION_DAYS)
    submissions = (
        ApplicationStepSubmission.objects.select_related("bootcamp_application")
        .exclude(
            Q(bootcamp_application__state__in=REVIEW_COMPLETED_APP_STATES)
            | Q(bootcamp_application__bootcamp_run__start_date__lte=now)
        )
        .filter(
            Q(submission_status=SUBMISSION_STATUS_PENDING)
            & Q(videointerviews__created_on__lte=cutoff_date)
        )
    )

    api.refresh_jobma_interview_submissions(submissions)
    # For reasons unknown, a few applications had interviews with null urls and/or no submissions.
    applications = BootcampApplication.objects.filter(
        Q(submissions__isnull=True)
        | Q(submissions__videointerviews__isnull=True)
        | Q(submissions__videointerviews__interview__interview_url__isnull=True)
    )
    for application in applications:
        submission = application.submissions.first()
        if submission and submission.content_object:
            submission.content_object.interview.delete()
        try:
            api.populate_interviews_in_jobma(application)
        except:  # pylint:disable=bare-except
            log.exception("Exception processing application %d", application.id)
