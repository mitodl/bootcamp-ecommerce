"""Tests for verification_api"""
from urllib.parse import quote_plus
import pytest

from django.core.mail import EmailMessage
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from django.test.client import RequestFactory

from mail.v2 import verification_api
from main.test_utils import any_instance_of
from profiles.models import ChangeEmailRequest

pytestmark = [pytest.mark.django_db]


def test_send_verification_email(mocker, rf):
    """Test that send_verification_email sends an email with the link in it"""
    from social_core.backends.email import EmailAuth
    from social_django.utils import load_backend, load_strategy

    send_messages_mock = mocker.patch("mail.v2.api.send_messages")
    email = "test@localhost"
    request = rf.post(reverse("social:complete", args=("email",)), {"email": email})
    # social_django depends on request.sesssion, so use the middleware to set that
    SessionMiddleware().process_request(request)
    strategy = load_strategy(request)
    backend = load_backend(strategy, EmailAuth.name, None)
    code = mocker.Mock(code="abc")
    verification_api.send_verification_email(strategy, backend, code, "def")

    send_messages_mock.assert_called_once_with([any_instance_of(EmailMessage)])

    email_body = send_messages_mock.call_args[0][0][0].body
    assert (
        "/create-account/confirm/?verification_code=abc&partial_token=def&backend=email"
        in email_body
    )


def test_send_verify_email_change_email(mocker, user):
    """Test email change request verification email sends with a link in it"""
    request = RequestFactory().get(reverse("account-settings"))
    change_request = ChangeEmailRequest.objects.create(
        user=user, new_email="abc@example.com"
    )

    send_messages_mock = mocker.patch("mail.v2.api.send_messages")

    verification_api.send_verify_email_change_email(request, change_request)

    send_messages_mock.assert_called_once_with([any_instance_of(EmailMessage)])

    url = "{}?verification_code={}".format(
        request.build_absolute_uri(reverse("account-confirm-email-change")),
        quote_plus(change_request.code),
    )

    email_body = send_messages_mock.call_args[0][0][0].body
    assert url in email_body
