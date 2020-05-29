"""Tests for applications API functionality"""
from decimal import Decimal

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from applications.api import (
    get_or_create_bootcamp_application,
    derive_application_state,
    process_upload_resume,
    InvalidApplicationException,
    set_submission_review_status,
    get_required_submission_type,
)
from applications.constants import (
    AppStates,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    SUBMISSION_QUIZ,
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
)
from ecommerce.factories import LineFactory
from ecommerce.models import Order
from klasses.factories import BootcampRunFactory, InstallmentFactory
from profiles.factories import ProfileFactory, UserFactory
from main.utils import now_in_utc


@pytest.mark.django_db
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
        bootcamp_run=bootcamp_run, user__profile=None, resume_file=None
    )
    assert derive_application_state(app) == AppStates.AWAITING_PROFILE_COMPLETION.value

    ProfileFactory.create(user=app.user)
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_RESUME.value

    app.resume_file = SimpleUploadedFile("resume.txt", b"these are the file contents!")
    app.save()
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.AWAITING_USER_SUBMISSIONS.value

    first_submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application=app, run_application_step=run_steps[0], review_status=None
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
        run_key=app.bootcamp_run.run_key,
        price=installment.amount,
    )
    app.refresh_from_db()
    assert derive_application_state(app) == AppStates.COMPLETE.value


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.django_db
@pytest.mark.parametrize(
    "review,other_submissions,other_steps,expected",
    [
        (REVIEW_STATUS_APPROVED, True, True, AppStates.AWAITING_USER_SUBMISSIONS.value),
        (
            REVIEW_STATUS_APPROVED,
            False,
            True,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
        ),
        (REVIEW_STATUS_APPROVED, False, False, AppStates.AWAITING_PAYMENT.value),
        (REVIEW_STATUS_REJECTED, False, False, AppStates.REJECTED.value),
    ],
)
def test_set_submission_review_status(review, other_submissions, other_steps, expected):
    """
    set_submission_review_status should set submission review and update application state
    """
    bootcamp_application = BootcampApplicationFactory(
        state=AppStates.AWAITING_SUBMISSION_REVIEW.value
    )
    submission = ApplicationStepSubmissionFactory(
        review_status=None,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
    )
    if other_submissions:
        application_step = BootcampRunApplicationStepFactory.create(
            bootcamp_run=bootcamp_application.bootcamp_run,
            application_step__bootcamp=bootcamp_application.bootcamp_run.bootcamp,
        )
        ApplicationStepSubmissionFactory.create(
            review_status=None,
            bootcamp_application=bootcamp_application,
            run_application_step=application_step,
        )
    if other_steps:
        BootcampRunApplicationStepFactory.create(
            bootcamp_run=bootcamp_application.bootcamp_run
        )

    set_submission_review_status(submission, review)
    assert submission.review_status == review
    assert bootcamp_application.state == expected


@pytest.mark.django_db
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
