"""Tests for applications API functionality"""
from decimal import Decimal

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile

from applications.api import (
    create_and_send_applicant_letter,
    email_letter,
    get_or_create_bootcamp_application,
    derive_application_state,
    get_required_submission_type,
    render_applicant_letter_text,
)
from applications.constants import (
    AppStates,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    SUBMISSION_QUIZ,
    LETTER_TYPE_APPROVED,
    LETTER_TYPE_REJECTED,
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicantLetterFactory,
    ApplicationStepSubmissionFactory,
)
from applications.models import ApplicantLetter
from ecommerce.factories import LineFactory
from ecommerce.models import Order
from klasses.factories import BootcampRunFactory, InstallmentFactory
from profiles.factories import ProfileFactory, UserFactory
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


def test_email_letter(settings, mocker):
    """email_letter should email an ApplicantLetter"""
    settings.MAILGUN_FROM_EMAIL = "from@testing.fake"
    settings.BOOTCAMP_REPLY_TO_ADDRESS = "to@testing.fake"
    settings.SITE_BASE_URL = "https://fake.url"

    subject = "subject"
    text_body = "text"
    html_body = "html"
    applicant_letter = ApplicantLetterFactory.create()
    render_patched = mocker.patch(
        "applications.api.render_email_templates",
        return_value=(subject, text_body, html_body),
    )
    send_patched = mocker.patch("applications.api.send_message")
    email_letter(applicant_letter)
    assert send_patched.call_count == 1
    anymail = send_patched.call_args[0][0]
    assert anymail.subject == subject
    assert anymail.body == text_body
    assert anymail.to == [applicant_letter.application.user.email]
    assert anymail.from_email == settings.MAILGUN_FROM_EMAIL
    assert anymail.extra_headers == {"Reply-To": settings.BOOTCAMP_REPLY_TO_ADDRESS}
    assert anymail.alternatives == [(html_body, "text/html")]
    render_patched.assert_called_once_with(
        "applicant_letter",
        {
            "content": applicant_letter.letter_text,
            "subject": applicant_letter.letter_subject,
            "base_url": settings.SITE_BASE_URL,
        },
    )


@pytest.mark.parametrize(
    "letter_type, expected_subject, field",
    [
        [LETTER_TYPE_APPROVED, "Welcome!", "acceptance_text"],
        [LETTER_TYPE_REJECTED, "Regarding your application", "rejection_text"],
    ],
)
def test_render_applicant_letter_text(
    letter_template_page, letter_type, expected_subject, field
):
    """render_applicant_letter_text should fill in template variables of LetterTemplatePage to create text for a letter"""
    setattr(letter_template_page, field, "Dear {{ first_name }}")
    letter_template_page.save()
    application = BootcampApplicationFactory.create()
    subject, text = render_applicant_letter_text(application, letter_type=letter_type)
    assert expected_subject == subject
    assert text == f"Dear {application.user.profile.first_and_last_names[0]}"


def test_create_and_send_applicant_letter(mocker):
    """create_and_send_applicant_letter should create the ApplicantLetter and then email it"""
    subject = "subject"
    text = "text"
    letter_type = "type"
    application = BootcampApplicationFactory.create()
    patched_render = mocker.patch(
        "applications.api.render_applicant_letter_text", return_value=(subject, text)
    )
    patched_email = mocker.patch("applications.api.email_letter")
    create_and_send_applicant_letter(application, letter_type=letter_type)
    letter = ApplicantLetter.objects.get()
    assert letter.letter_type == letter_type
    assert letter.application == application
    assert letter.letter_subject == subject
    assert letter.letter_text == text
    patched_email.assert_called_once_with(letter)
    patched_render.assert_called_once_with(application, letter_type=letter_type)
