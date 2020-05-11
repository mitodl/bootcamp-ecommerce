"""Tests for applications API functionality"""
import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from applications.api import get_or_create_bootcamp_application, derive_application_state, process_upload_resume, \
    InvalidApplicationException
from applications.constants import (
    AppStates, REVIEW_STATUS_APPROVED, REVIEW_STATUS_REJECTED
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
)
from ecommerce.factories import OrderFactory
from ecommerce.models import Order
from klasses.factories import BootcampRunFactory
from profiles.constants import FEMALE
from profiles.factories import ProfileFactory, UserFactory
from main.utils import now_in_utc


@pytest.mark.django_db
def test_derive_application_state():
    """derive_application_state should return the correct state based on the bootcamp application and related data"""
    bootcamp_run = BootcampRunFactory.create()
    run_steps = BootcampRunApplicationStepFactory.create_batch(
        2,
        bootcamp_run=bootcamp_run
    )

    app = BootcampApplicationFactory.create(
        bootcamp_run=bootcamp_run,
        user__profile=None,
        resume_file=None,
        order=None,
    )
    assert derive_application_state(app) == AppStates.AWAITING_PROFILE_COMPLETION.value

    ProfileFactory.create(user=app.user, company="MIT", gender=FEMALE, birth_year=2000, job_title="Engineer")
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_RESUME.value

    app.resume_file = SimpleUploadedFile(
        "resume.txt",
        b"these are the file contents!"
    )
    app.save()
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_USER_SUBMISSIONS.value

    first_submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application=app,
        run_application_step=run_steps[0],
        review_status=None
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

    app.order = OrderFactory.create(status=Order.FULFILLED, user=app.user)
    app.save()
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.COMPLETE.value


@pytest.mark.django_db
def test_derive_application_state_rejected():
    """derive_application_state should return the rejected state if any of the user's submissions were rejected"""
    run_step = BootcampRunApplicationStepFactory.create()
    app = BootcampApplicationFactory.create(
        bootcamp_run=run_step.bootcamp_run,
        resume_file=SimpleUploadedFile(
            "resume.txt",
            b"these are the file contents!"
        )
    )
    ApplicationStepSubmissionFactory.create(
        bootcamp_application=app,
        run_application_step=run_step,
        review_status=REVIEW_STATUS_REJECTED,
        review_status_date=now_in_utc(),
    )
    assert derive_application_state(app) == AppStates.REJECTED.value


@pytest.mark.django_db
def test_get_or_create_bootcamp_application(mocker):
    """
    get_or_create_bootcamp_application should fetch an existing bootcamp application, or create one with the \
    application state set properly
    """
    patched_derive_state = mocker.patch(
        "applications.api.derive_application_state", return_value=AppStates.COMPLETE.value
    )
    users = UserFactory.create_batch(2)
    bootcamp_runs = BootcampRunFactory.create_batch(2)
    bootcamp_app = get_or_create_bootcamp_application(bootcamp_run=bootcamp_runs[0], user=users[0])
    patched_derive_state.assert_called_once_with(bootcamp_app)
    assert bootcamp_app.bootcamp_run == bootcamp_runs[0]
    assert bootcamp_app.user == users[0]
    assert bootcamp_app.state == patched_derive_state.return_value
    # The function should just return the existing application if one exists already
    existing_app = BootcampApplicationFactory.create(
        user=users[1],
        bootcamp_run=bootcamp_runs[1]
    )
    bootcamp_app = get_or_create_bootcamp_application(bootcamp_run=bootcamp_runs[1], user=users[1])
    assert bootcamp_app == existing_app


@pytest.mark.django_db
def test_process_upload_resume():
    """
    process_upload_resume should raise an exception if in wrong state
    """
    existing_app = BootcampApplicationFactory(state=AppStates.AWAITING_PROFILE_COMPLETION)
    resume_file = SimpleUploadedFile('resume.pdf', b'file_content')
    with pytest.raises(InvalidApplicationException):
        process_upload_resume(resume_file, existing_app)
