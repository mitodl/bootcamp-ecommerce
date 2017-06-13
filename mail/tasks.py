"""
Tasks for mail app
"""
import logging
from decimal import Decimal

from django.conf import settings

from bootcamp.celery import app
from ecommerce.models import Line
from klasses.models import Klass, BootcampAdmissionCache
from mail.api import MailgunClient
from mail.models import AutomaticReminderEmail, SentAutomaticEmails

log = logging.getLogger(__name__)


def send_reminder_payment_emails():
    """
    Checks if there are klasses that have an installment coming and
    sends an email to all the users who need to be reminded of paying
    if the deadline is in X days (where X is defined in the AutomaticReminderEmail)
    """
    reminder_email_in_days = list(AutomaticReminderEmail.objects.filter(
        reminder_type=AutomaticReminderEmail.PAYMENT_APPROACHING).values_list('days_before', flat=True))
    klasses_reminder = []
    for klass in Klass.objects.all():
        if klass.next_payment_deadline_days in reminder_email_in_days:
            klasses_reminder.append(klass)
    if not klasses_reminder:
        return

    for klass in klasses_reminder:
        recipients_context = []
        recipients_users = []
        email_template = AutomaticReminderEmail.objects.filter(days_before=klass.next_payment_deadline_days).first()
        all_admissions = BootcampAdmissionCache.objects.filter(klass=klass)
        for admission in all_admissions:
            user = admission.user
            if SentAutomaticEmails.objects.filter(user=user, automatic_email=email_template, klass=klass).exists():
                # reminder already sent
                continue
            total_already_paid = Line.total_paid_for_klass(user, klass.klass_key).get('total') or Decimal('0.00')
            remaining_balance = klass.total_due_by_next_deadline - total_already_paid
            if remaining_balance <= 0:
                # amount already paid
                continue
            recipients_context.append(
                {
                    'email': user.email,
                    'full_name': user.profile.name,
                    'bootcamp_name': klass.display_title,
                    'remaining_balance': str(remaining_balance),
                    'payment_due_date': klass.next_installment.deadline.strftime('%b %d %Y'),
                    'site_URL': settings.BOOTCAMP_ECOMMERCE_BASE_URL,
                }
            )
            recipients_users.append(user)

        try:
            MailgunClient.send_batch(
                email_template.email_subject,
                email_template.email_body,
                [(context['email'], context) for context in recipients_context],
                raise_for_status=True,
            )
        except:  # pylint: disable=bare-except
            log.exception('Impossible to send pay reminder email for %s', klass.display_title)
            continue

        SentAutomaticEmails.objects.bulk_create(
            SentAutomaticEmails(
                user=user,
                automatic_email=email_template,
                klass=klass,
            ) for user in recipients_users
        )


@app.task
def async_send_reminder_payment_emails():
    """
    Takes care of calling the function to send payment reminders
    """
    return send_reminder_payment_emails()
