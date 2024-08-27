"""Tests for functions sending email relating to applications"""

import pytest

from applications.constants import LETTER_TYPE_APPROVED, LETTER_TYPE_REJECTED
from applications.factories import ApplicantLetterFactory, BootcampApplicationFactory
from applications.mail_api import (
    create_and_send_applicant_letter,
    email_letter,
    render_applicant_letter_text,
)
from applications.models import ApplicantLetter

pytestmark = pytest.mark.django_db


def test_email_letter(settings, mocker, letter_template_page):
    """email_letter should email an ApplicantLetter"""
    settings.MAILGUN_FROM_EMAIL = "from@testing.fake"
    settings.BOOTCAMP_REPLY_TO_ADDRESS = "to@testing.fake"
    settings.SITE_BASE_URL = "https://fake.url"

    subject = "subject"
    text_body = "text"
    html_body = "html"
    applicant_letter = ApplicantLetterFactory.create()
    render_patched = mocker.patch(
        "applications.mail_api.render_email_templates",
        return_value=(subject, text_body, html_body),
    )
    send_patched = mocker.patch("applications.mail_api.send_message")
    signatory = {
        "name": letter_template_page.signatory_name,
        "image": letter_template_page.signature_image,
    }
    email_letter(applicant_letter, signatory)
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
            "signatory": signatory,
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
    subject, text, signatory = render_applicant_letter_text(
        application, letter_type=letter_type
    )
    assert expected_subject == subject
    assert text == f"Dear {application.user.legal_address.first_name}"
    assert signatory["name"] == letter_template_page.signatory_name
    assert signatory["image"] == letter_template_page.signature_image


def test_create_and_send_applicant_letter(mocker):
    """create_and_send_applicant_letter should create the ApplicantLetter and then email it"""
    subject = "subject"
    text = "text"
    letter_type = "type"
    application = BootcampApplicationFactory.create()
    patched_render = mocker.patch(
        "applications.mail_api.render_applicant_letter_text",
        return_value=(subject, text, {}),
    )
    patched_email = mocker.patch("applications.mail_api.email_letter")
    create_and_send_applicant_letter(application, letter_type=letter_type)
    letter = ApplicantLetter.objects.get()
    assert letter.letter_type == letter_type
    assert letter.application == application
    assert letter.letter_subject == subject
    assert letter.letter_text == text
    patched_email.assert_called_once_with(letter, {})
    patched_render.assert_called_once_with(application, letter_type=letter_type)
