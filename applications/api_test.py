"""Tests for applications API functionality"""
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from applications.api import (
    get_or_create_bootcamp_application,
    derive_application_state,
    get_required_submission_type,
    populate_interviews_in_jobma,
)
from applications.constants import (
    AppStates,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    SUBMISSION_QUIZ,
    SUBMISSION_VIDEO,
)
from applications.factories import (
    ApplicationStepFactory,
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
)
from applications.models import ApplicationStepSubmission, VideoInterviewSubmission
from ecommerce.factories import LineFactory
from ecommerce.models import Order
from klasses.factories import BootcampRunFactory, InstallmentFactory
from jobma.factories import InterviewFactory, JobFactory
from jobma.models import Interview
from profiles.factories import ProfileFactory, UserFactory, LegalAddressFactory
from main.utils import now_in_utc


pytestmark = pytest.mark.django_db


def test_derive_application_state():
    """derive_application_state should return the correct state based on the bootcamp application and related data"""
    bootcamp_run = BootcampRunFactory.create()
    installment = InstallmentFactory.create(
        bootcamp_run=bootcamp_run, amount=Decimal("100")
    )
    run_steps = BootcampRunApplicationStepFactory.create_batch(
        2, bootcamp_run=bootcamp_run
    )

    app = BootcampApplicationFactory.create(
        bootcamp_run=bootcamp_run,
        user__profile=None,
        user__legal_address=None,
        resume_file=None,
    )
    assert derive_application_state(app) == AppStates.AWAITING_PROFILE_COMPLETION.value

    ProfileFactory.create(user=app.user)
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_PROFILE_COMPLETION.value
    LegalAddressFactory.create(user=app.user)
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_RESUME.value

    app.resume_file = SimpleUploadedFile("resume.txt", b"these are the file contents!")
    app.save()
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_USER_SUBMISSIONS.value

    first_submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application=app, run_application_step=run_steps[0], is_pending=True
    )
    assert derive_application_state(app) == AppStates.AWAITING_SUBMISSION_REVIEW.value

    first_submission.review_status = REVIEW_STATUS_APPROVED
    first_submission.save()
    # The user should only be allowed to pay after *all* of the required submissions have been reviewed
    assert derive_application_state(app) == AppStates.AWAITING_USER_SUBMISSIONS.value

    ApplicationStepSubmissionFactory.create(
        bootcamp_application=app,
        run_application_step=run_steps[1],
        review_status=REVIEW_STATUS_APPROVED,
        review_status_date=now_in_utc(),
    )
    assert derive_application_state(app) == AppStates.AWAITING_PAYMENT.value

    LineFactory.create(
        order__status=Order.FULFILLED,
        order__user=app.user,
        order__application=app,
        order__total_price_paid=installment.amount,
        run_key=app.bootcamp_run.run_key,
        price=installment.amount,
    )
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.COMPLETE.value


def test_derive_application_state_rejected():
    """derive_application_state should return the rejected state if any of the user's submissions were rejected"""
    run_step = BootcampRunApplicationStepFactory.create()
    app = BootcampApplicationFactory.create(
        bootcamp_run=run_step.bootcamp_run,
        resume_file=SimpleUploadedFile("resume.txt", b"these are the file contents!"),
    )
    ApplicationStepSubmissionFactory.create(
        bootcamp_application=app,
        run_application_step=run_step,
        review_status=REVIEW_STATUS_REJECTED,
        review_status_date=now_in_utc(),
    )
    assert derive_application_state(app) == AppStates.REJECTED.value


def test_get_or_create_bootcamp_application(mocker):
    """
    get_or_create_bootcamp_application should fetch an existing bootcamp application, or create one with the \
    application state set properly
    """
    patched_derive_state = mocker.patch(
        "applications.api.derive_application_state",
        return_value=AppStates.COMPLETE.value,
    )
    users = UserFactory.create_batch(2)
    bootcamp_runs = BootcampRunFactory.create_batch(2)
    bootcamp_app, created = get_or_create_bootcamp_application(
        bootcamp_run_id=bootcamp_runs[0].id, user=users[0]
    )
    patched_derive_state.assert_called_once_with(bootcamp_app)
    assert bootcamp_app.bootcamp_run == bootcamp_runs[0]
    assert bootcamp_app.user == users[0]
    assert bootcamp_app.state == patched_derive_state.return_value
    assert created is True
    # The function should just return the existing application if one exists already
    existing_app = BootcampApplicationFactory.create(
        user=users[1], bootcamp_run=bootcamp_runs[1]
    )
    bootcamp_app, created = get_or_create_bootcamp_application(
        bootcamp_run_id=bootcamp_runs[1].id, user=users[1]
    )
    assert bootcamp_app == existing_app
    assert created is False


def test_get_required_submission_type(awaiting_submission_app):
    """ Test that get_required_submission_type returns the correct submission type"""

    # New application for a bootcamp with no steps at all
    stepless_app = BootcampApplicationFactory.create()
    assert get_required_submission_type(stepless_app) is None

    # The fixture has 2 steps (Video, Quiz) and first step has been submitted
    assert (
        get_required_submission_type(awaiting_submission_app.application)
        == SUBMISSION_QUIZ
    )

    # After submitting all required steps, no type should be returned
    ApplicationStepSubmissionFactory.create(
        bootcamp_application=awaiting_submission_app.application,
        run_application_step=awaiting_submission_app.run_steps[1],
    )
    assert get_required_submission_type(awaiting_submission_app.application) is None


@pytest.fixture
def application():
    """Application for a user"""
    yield BootcampApplicationFactory.create()


@pytest.fixture
def job(application):  # pylint: disable=redefined-outer-name
    """Make a job"""
    yield JobFactory.create(run=application.bootcamp_run)


@pytest.mark.parametrize("interview_exists", [True, False])
@pytest.mark.parametrize("has_interview_link", [True, False])
def test_populate_interviews_in_jobma(
    interview_exists, has_interview_link, mocker, application, job
):  # pylint: disable=redefined-outer-name,too-many-arguments
    """
    populate_interviews_in_jobma should create interviews on Jobma via REST API
    for each relevant BootcampRunApplicationStep
    """
    video_app_step = ApplicationStepFactory.create(
        bootcamp=application.bootcamp_run.bootcamp, submission_type=SUBMISSION_VIDEO
    )
    # this step should be ignored since it's not a video
    quiz_app_step = ApplicationStepFactory.create(
        bootcamp=application.bootcamp_run.bootcamp, submission_type=SUBMISSION_QUIZ
    )
    for step in (video_app_step, quiz_app_step):
        BootcampRunApplicationStepFactory.create(
            bootcamp_run=application.bootcamp_run, application_step=step
        )

    new_interview_link = "http://fake.interview.link"
    create_interview = mocker.patch(
        "applications.api.create_interview_in_jobma", return_value=new_interview_link
    )

    if interview_exists:
        interview = InterviewFactory.create(job=job, applicant=application.user)
        if not has_interview_link:
            interview.interview_url = None
            interview.save()

    populate_interviews_in_jobma(application)
    # We should be able to run this repeatedly without creating duplicate objects in the database
    populate_interviews_in_jobma(application)

    if not interview_exists or not has_interview_link:
        interview = Interview.objects.get(job=job, applicant=application.user)
        create_interview.assert_any_call(interview)
        assert create_interview.call_count == 2

        video_submission = VideoInterviewSubmission.objects.get(interview=interview)
        step_submission = ApplicationStepSubmission.objects.get()
        assert step_submission.content_object == video_submission
    else:
        create_interview.assert_not_called()
