"""API for bootcamp applications app"""
from anymail.message import AnymailMessage
from django.conf import settings
from django.core import mail
from django.db import transaction

from applications.constants import (
    AppStates,
    LETTER_TYPE_APPROVED,
    LETTER_TYPE_REJECTED,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_PENDING,
)
from cms.api import render_template
from cms.models import LetterTemplatePage
from mail.v2.api import render_email_templates, send_message


@transaction.atomic
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
    from applications.models import BootcampApplication

    bootcamp_app, created = BootcampApplication.objects.select_for_update().get_or_create(
        user=user, bootcamp_run_id=bootcamp_run_id
    )
    if created:
        derived_state = derive_application_state(bootcamp_app)
        bootcamp_app.state = derived_state
        bootcamp_app.save()
    return bootcamp_app, created


def derive_application_state(
    bootcamp_application
):  # pylint: disable=too-many-return-statements
    """
    Returns the correct state that an application should be in based on the application object itself and related data

    Args:
        bootcamp_application (BootcampApplication): A bootcamp application

    Returns:
        str: The derived state of the bootcamp application based on related data
    """
    if (
        not hasattr(bootcamp_application.user, "profile")
        or not bootcamp_application.user.profile.is_complete
    ):
        return AppStates.AWAITING_PROFILE_COMPLETION.value
    if not bootcamp_application.resume_file:
        return AppStates.AWAITING_RESUME.value
    submissions = list(bootcamp_application.submissions.all())
    submission_review_statuses = [
        submission.review_status for submission in submissions
    ]
    if any([status == REVIEW_STATUS_REJECTED for status in submission_review_statuses]):
        return AppStates.REJECTED.value
    elif any(
        [status == REVIEW_STATUS_PENDING for status in submission_review_statuses]
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


def email_letter(applicant_letter):
    """
    Email the applicant letter

    Args:
        applicant_letter (ApplicantLetter): The rendered applicant letter in the database
    """

    subject, text_body, html_body = render_email_templates(
        "applicant_letter",
        {
            "content": applicant_letter.letter_text,
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

    profile = application.user.profile
    first_name, last_name = profile.first_and_last_names
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

    return subject, rendered_text


def create_and_send_applicant_letter(application, *, letter_type):
    """
    Email the applicant about their admission status, and store the text to be viewed via LettersView.

    Args:
        application (BootcampApplication): The application
        letter_type (str): The type of letter to be rendered
    """
    from applications.models import ApplicantLetter

    subject, text = render_applicant_letter_text(application, letter_type=letter_type)
    letter = ApplicantLetter.objects.create(
        application=application,
        letter_text=text,
        letter_subject=subject,
        letter_type=letter_type,
    )
    email_letter(letter)
