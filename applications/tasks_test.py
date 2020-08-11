"""Tests for application tasks"""
from datetime import timedelta

import pytest

from applications.constants import (
    AppStates,
    SUBMISSION_STATUS_PENDING,
    SUBMISSION_STATUS_SUBMITTED,
    SUBMISSION_VIDEO,
)
from applications.factories import (
    BootcampApplicationFactory,
    VideoInterviewSubmissionFactory,
    ApplicationStepSubmissionFactory,
    ApplicationStepFactory,
    BootcampRunApplicationStepFactory,
)
from applications.tasks import (
    create_and_send_applicant_letter,
    refresh_pending_interview_links,
)
from ecommerce.test_utils import create_test_application
from jobma.factories import InterviewFactory, JobFactory
from jobma.models import Interview
from klasses.factories import BootcampRunFactory
from main.utils import now_in_utc

pytestmark = pytest.mark.django_db


@pytest.fixture
def application():
    """An application for testing"""
    yield create_test_application()


def test_create_and_send_applicant_letter(
    mocker, application
):  # pylint: disable=redefined-outer-name
    """This should just start a task to forward the request to the API function"""
    letter_type = "letter_type"
    patched = mocker.patch("applications.mail_api.create_and_send_applicant_letter")

    create_and_send_applicant_letter.delay(
        application_id=application.id, letter_type=letter_type
    )
    patched.assert_called_once_with(application, letter_type=letter_type)


@pytest.mark.parametrize(
    "state,status,old_link,old_run,recreated",
    [
        [
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            SUBMISSION_STATUS_PENDING,
            True,
            False,
            True,
        ],
        [
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            SUBMISSION_STATUS_PENDING,
            True,
            True,
            False,
        ],
        [
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            SUBMISSION_STATUS_PENDING,
            False,
            False,
            False,
        ],
        [
            AppStates.AWAITING_PAYMENT.value,
            SUBMISSION_STATUS_PENDING,
            True,
            False,
            False,
        ],
        [
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            SUBMISSION_STATUS_SUBMITTED,
            True,
            False,
            False,
        ],
    ],
)  # pylint:disable=too-many-locals
def test_refresh_pending_interview_links(  # pylint:disable=too-many-arguments
    mocker, settings, state, status, old_link, old_run, recreated
):
    """ Test that refresh_pending_interview_links updates links only when appropriate """
    now = now_in_utc()
    settings.JOBMA_LINK_EXPIRATION_DAYS = 0 if old_link else 30
    mock_log = mocker.patch("applications.tasks.log.debug")
    create_interview = mocker.patch(
        "applications.api.create_interview_in_jobma",
        return_value="http://fake.interview.link",
    )

    run = BootcampRunFactory.create(
        start_date=(now + timedelta(days=(-10 if old_run else 10)))
    )
    bootcamp_app = BootcampApplicationFactory.create(state=state, bootcamp_run=run)
    video_app_step = ApplicationStepFactory.create(
        bootcamp=bootcamp_app.bootcamp_run.bootcamp, submission_type=SUBMISSION_VIDEO
    )
    application_step = BootcampRunApplicationStepFactory.create(
        bootcamp_run=bootcamp_app.bootcamp_run, application_step=video_app_step
    )
    interview = InterviewFactory.create(
        job=JobFactory.create(run=bootcamp_app.bootcamp_run),
        applicant=bootcamp_app.user,
    )
    interview_submission = VideoInterviewSubmissionFactory.create(interview=interview)
    submission = ApplicationStepSubmissionFactory.create(
        run_application_step=application_step,
        bootcamp_application=bootcamp_app,
        is_pending=True,
        content_object=interview_submission,
        submission_status=status,
    )
    assert submission.videointerviews.first() == interview_submission
    refresh_pending_interview_links()

    new_interview = Interview.objects.get(applicant=bootcamp_app.user)
    if recreated:
        assert create_interview.call_count == 1
        assert new_interview.id != interview.id
        mock_log.assert_called_once_with(
            "Interview recreated for submission %d, application %d, user %s",
            submission.id,
            bootcamp_app.id,
            bootcamp_app.user.email,
        )
    else:
        mock_log.assert_not_called()
        assert new_interview.id == interview.id
