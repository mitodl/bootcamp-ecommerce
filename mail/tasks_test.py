"""
Tests for task module
"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest
from django.conf import settings
from pytz import UTC
from requests import Response
from rest_framework import status

from ecommerce.factories import LineFactory, OrderFactory
from klasses.factories import BootcampAdmissionCacheFactory, InstallmentFactory
from mail import tasks
from mail.models import AutomaticReminderEmail, SentAutomaticEmails
from profiles.factories import ProfileFactory


# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access

pytestmark = pytest.mark.django_db


def test_task_passthrough(mocker):
    """
    Test that async_send_reminder_payment_emails calls send_reminder_payment_emails
    """
    mocked_func = mocker.patch('mail.tasks.send_reminder_payment_emails', autospec=True)
    tasks.async_send_reminder_payment_emails.delay()
    mocked_func.assert_called_once_with()


@pytest.fixture()
def test_data():
    """
    Sets up the data for the tests in this module
    """
    # be sure the data in the database is what is expected
    assert list(AutomaticReminderEmail.objects.filter(
        reminder_type=AutomaticReminderEmail.PAYMENT_APPROACHING).values_list('days_before', flat=True)) == [7, 2, 0]

    user_1 = ProfileFactory.create().user
    user_2 = ProfileFactory.create().user
    admission_cache = BootcampAdmissionCacheFactory.create(user=user_1)
    klass = admission_cache.klass
    BootcampAdmissionCacheFactory.create(user=user_2, klass=klass)
    next_installment = InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(days=2, hours=1))
    InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(days=7, hours=1))

    email_template = AutomaticReminderEmail.objects.filter(
        reminder_type=AutomaticReminderEmail.PAYMENT_APPROACHING, days_before=2).first()

    return (user_1, user_2,), klass, next_installment, email_template


@pytest.fixture()
def mocked_send_batch(mocker):
    """
    Mocking the Mailgun client function
    """
    mocked_func = mocker.patch(
        'mail.api.MailgunClient.send_batch',
        new_callable=MagicMock,
        return_value=Mock(
            spec=Response,
            status_code=status.HTTP_200_OK,
        )
    )
    return mocked_func


def test_happy_path(test_data, mocked_send_batch):
    """
    Test that an email is sent to each student admitted
    """
    users, klass, next_installment, email_template = test_data
    assert SentAutomaticEmails.objects.all().exists() is False

    tasks.send_reminder_payment_emails()

    assert SentAutomaticEmails.objects.count() == 2
    for mail_sent in SentAutomaticEmails.objects.all():
        assert mail_sent.user in users
        assert mail_sent.klass == klass

    recipients_context = []
    for user in users:
        recipients_context.append(
            {
                'email': user.email,
                'full_name': user.profile.name,
                'bootcamp_name': klass.display_title,
                'remaining_balance': str(next_installment.amount),
                'payment_due_date': klass.next_installment.deadline.strftime('%b %d %Y'),
                'site_URL': settings.BOOTCAMP_ECOMMERCE_BASE_URL,
            }
        )
    mocked_send_batch.assert_called_once_with(
        email_template.email_subject,
        email_template.email_body,
        [(context['email'], context) for context in recipients_context],
        raise_for_status=True,
    )


def test_next_deadline_not_in_range(test_data, mocked_send_batch):
    """
    Test that nothing happens if the next payment deadline is not
    in the list of number of days configured in AutomaticReminderEmail
    """
    _, _, next_installment, _ = test_data
    next_installment.deadline = datetime.now(tz=UTC)+timedelta(days=3, hours=1)
    next_installment.save()

    tasks.send_reminder_payment_emails()

    assert SentAutomaticEmails.objects.all().exists() is False
    assert mocked_send_batch.call_count == 0


def test_send_email_only_if_not_already_sent(test_data, mocked_send_batch):
    """
    Tests that an email is sent only if not already sent
    """
    users, klass, next_installment, email_template = test_data
    SentAutomaticEmails.objects.create(user=users[0], klass=klass, automatic_email=email_template)

    tasks.send_reminder_payment_emails()

    assert SentAutomaticEmails.objects.count() == 2
    assert SentAutomaticEmails.objects.filter(user=users[1], klass=klass).exists()
    mocked_send_batch.assert_called_once_with(
        email_template.email_subject,
        email_template.email_body,
        [
            (
                users[1].email,
                {
                    'email': users[1].email,
                    'full_name': users[1].profile.name,
                    'bootcamp_name': klass.display_title,
                    'remaining_balance': str(next_installment.amount),
                    'payment_due_date': klass.next_installment.deadline.strftime('%b %d %Y'),
                    'site_URL': settings.BOOTCAMP_ECOMMERCE_BASE_URL,
                }
            )
        ],
        raise_for_status=True,
    )


def test_send_email_if_need_to_pay(test_data, mocked_send_batch):
    """
    Tests that an email is sent only if the expected amount has not been yet paid
    """
    users, klass, next_installment, email_template = test_data
    order = OrderFactory.create(user=users[0], status='fulfilled')
    LineFactory.create(order=order, klass_key=klass.klass_key, price=next_installment.amount+100)

    tasks.send_reminder_payment_emails()

    assert SentAutomaticEmails.objects.count() == 1
    assert SentAutomaticEmails.objects.filter(user=users[1], klass=klass).exists()
    mocked_send_batch.assert_called_once_with(
        email_template.email_subject,
        email_template.email_body,
        [
            (
                users[1].email,
                {
                    'email': users[1].email,
                    'full_name': users[1].profile.name,
                    'bootcamp_name': klass.display_title,
                    'remaining_balance': str(next_installment.amount),
                    'payment_due_date': klass.next_installment.deadline.strftime('%b %d %Y'),
                    'site_URL': settings.BOOTCAMP_ECOMMERCE_BASE_URL,
                }
            )
        ],
        raise_for_status=True,
    )


def test_error_from_mailgun(test_data, mocked_send_batch):
    """
    Tests if an email to mailgun has not been accepted, is is considered as never sent
    """
    mocked_send_batch.side_effect = ZeroDivisionError
    tasks.send_reminder_payment_emails()
    assert SentAutomaticEmails.objects.all().exists() is False
