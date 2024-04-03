"""Functions for sending email relating to applications"""

from anymail.message import AnymailMessage
from django.conf import settings
from django.core import mail

from applications.constants import LETTER_TYPE_APPROVED, LETTER_TYPE_REJECTED
from cms.api import render_template
from cms.models import LetterTemplatePage
from mail.v2.api import render_email_templates, send_message
from profiles.api import get_first_and_last_names


def email_letter(applicant_letter, signatory):
    """
    Email the applicant letter

    Args:
        applicant_letter (ApplicantLetter): The rendered applicant letter in the database
        signatory (dict): The signatory name and signature
    """

    subject, text_body, html_body = render_email_templates(
        "applicant_letter",
        {
            "content": applicant_letter.letter_text,
            "signatory": signatory,
            "subject": applicant_letter.letter_subject,
            "base_url": settings.SITE_BASE_URL,
        },
    )
    with mail.get_connection(settings.NOTIFICATION_EMAIL_BACKEND) as connection:
        msg = AnymailMessage(
            subject=subject,
            body=text_body,
            to=[applicant_letter.application.user.email],
            from_email=settings.MAILGUN_FROM_EMAIL,
            connection=connection,
            headers={"Reply-To": settings.BOOTCAMP_REPLY_TO_ADDRESS},
        )
        msg.attach_alternative(html_body, "text/html")
        send_message(msg)


def render_applicant_letter_text(application, *, letter_type):
    """
    Render the text for the applicant letter

    Args:
        application (BootcampApplication): The application
        letter_type (str): Type of letter to send

    Returns:
        (str, str): The subject and text
    """
    # Should be created beforehand, and should be limited to one by wagtail
    page = LetterTemplatePage.objects.get()

    if letter_type == LETTER_TYPE_APPROVED:
        template_text = page.acceptance_text
        subject = "Welcome!"
    elif letter_type == LETTER_TYPE_REJECTED:
        template_text = page.rejection_text
        subject = "Regarding your application"
    else:
        raise ValueError(f"Unexpected letter type {letter_type}")

    first_name, last_name = get_first_and_last_names(application.user)
    rendered_text = render_template(
        text=template_text,
        context={
            "first_name": first_name,
            "last_name": last_name,
            "bootcamp_name": application.bootcamp_run.bootcamp.title,
            "bootcamp_start_date": application.bootcamp_run.start_date.strftime(
                "%b %d, %Y"
            ),
            "price": "${:,.2f}".format(application.price),
        },
    )

    signatory_details = {"name": page.signatory_name, "image": page.signature_image}

    return subject, rendered_text, signatory_details


def create_and_send_applicant_letter(application, *, letter_type):
    """
    Email the applicant about their admission status, and store the text to be viewed via LettersView.

    Args:
        application (BootcampApplication): The application
        letter_type (str): The type of letter to be rendered
    """
    from applications.models import ApplicantLetter

    subject, text, signatory = render_applicant_letter_text(
        application, letter_type=letter_type
    )
    letter = ApplicantLetter.objects.create(
        application=application,
        letter_text=text,
        letter_subject=subject,
        letter_type=letter_type,
    )
    email_letter(letter, signatory)
