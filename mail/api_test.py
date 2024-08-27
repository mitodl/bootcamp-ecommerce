"""
Test cases for email API
"""

import json
import string

import pytest
from django.core.exceptions import ImproperlyConfigured
from requests import Response
from requests.exceptions import HTTPError
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from mail.api import MailgunClient
from mail.exceptions import SendBatchException

pytestmark = pytest.mark.django_db


@pytest.fixture
def mocked_json():
    """Mocked version of the json method for the Response class"""

    def _json(*args, **kwargs):
        return {}

    yield _json


batch_recipient_arg = [("a@example.com", None), ("b@example.com", {"name": "B"})]
individual_recipient_arg = "a@example.com"


@pytest.fixture
def mock_post(mocker, mocked_json):
    """Mock post with successful json response"""
    mocked = mocker.patch(
        "requests.post",
        autospec=True,
        return_value=mocker.Mock(
            spec=Response, status_code=HTTP_200_OK, json=mocked_json
        ),
    )
    yield mocked


@pytest.mark.parametrize("sender_name", [None, "Tester"])
def test_send_batch(settings, sender_name, mock_post):
    """
    Test that MailgunClient.send_batch sends expected parameters to the Mailgun API
    Base case with only one batch call to the Mailgun API.
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    MailgunClient.send_batch(
        "email subject", "email body", batch_recipient_arg, sender_name=sender_name
    )
    assert mock_post.called is True
    called_args, called_kwargs = mock_post.call_args
    assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
    assert called_kwargs["auth"] == ("api", settings.MAILGUN_KEY)
    assert called_kwargs["data"]["text"].startswith("email body")
    assert called_kwargs["data"]["subject"] == "email subject"
    assert sorted(called_kwargs["data"]["to"]) == sorted(
        [email for email, _ in batch_recipient_arg]
    )
    assert called_kwargs["data"]["recipient-variables"] == json.dumps(
        {"a@example.com": {}, "b@example.com": {"name": "B"}}
    )
    if sender_name is not None:
        assert called_kwargs["data"]["from"] == "{sender_name} <{email}>".format(
            sender_name=sender_name, email=settings.EMAIL_SUPPORT
        )

    else:
        assert called_kwargs["data"]["from"] == settings.EMAIL_SUPPORT


def test_send_batch_recipient_override(settings, mock_post):
    """
    Test that MailgunClient.send_batch works properly with recipient override enabled
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = "recipient@override.com"
    MailgunClient.send_batch(
        "subject", "body", batch_recipient_arg, sender_name="sender"
    )
    assert mock_post.called is True
    called_args, called_kwargs = mock_post.call_args
    assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
    assert called_kwargs["auth"] == ("api", settings.MAILGUN_KEY)
    assert (
        called_kwargs["data"]["text"]
        == """body

[overridden recipient]
a@example.com: {}
b@example.com: {"name": "B"}"""
    )
    assert called_kwargs["data"]["subject"] == "subject"
    assert called_kwargs["data"]["to"] == ["recipient@override.com"]
    assert called_kwargs["data"]["recipient-variables"] == json.dumps(
        {"recipient@override.com": {}}
    )
    assert called_kwargs["data"]["from"] == "sender <support@example.com>"


def test_send_batch_chunk(settings, mock_post):
    """
    Test that MailgunClient.send_batch chunks recipients
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    chunk_size = 10
    recipient_tuples = [
        ("{0}@example.com".format(letter), None)  # noqa: UP030
        for letter in string.ascii_letters
    ]
    chunked_emails_to = [
        recipient_tuples[i : i + chunk_size]
        for i in range(0, len(recipient_tuples), chunk_size)
    ]
    assert len(recipient_tuples) == 52
    responses = MailgunClient.send_batch(
        "email subject", "email body", recipient_tuples, chunk_size=chunk_size
    )
    assert mock_post.called is True
    assert mock_post.call_count == 6
    for call_num, args in enumerate(mock_post.call_args_list):
        called_args, called_kwargs = args
        assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
        assert called_kwargs["data"]["text"].startswith("email body")
        assert called_kwargs["data"]["subject"] == "email subject"
        assert sorted(called_kwargs["data"]["to"]) == sorted(
            [email for email, _ in chunked_emails_to[call_num]]
        )
        assert called_kwargs["data"]["recipient-variables"] == json.dumps(
            {email: context or {} for email, context in chunked_emails_to[call_num]}
        )

        response = responses[call_num]
        assert response.status_code == HTTP_200_OK


@pytest.mark.parametrize("recipient_override", [None, "recipient_override@example.com"])
def test_send_batch_error(settings, recipient_override, mock_post):
    """
    Test that MailgunClient.send_batch returns a non-zero error code where the mailgun API returns a non-zero code
    """
    mock_post.return_value = Response()
    mock_post.return_value.status_code = HTTP_400_BAD_REQUEST

    chunk_size = 10
    recipient_tuples = [
        ("{0}@example.com".format(letter), {"letter": letter})  # noqa: UP030
        for letter in string.ascii_letters
    ]
    chunked_emails_to = [
        recipient_tuples[i : i + chunk_size]
        for i in range(0, len(recipient_tuples), chunk_size)
    ]
    assert len(recipient_tuples) == 52
    settings.MAILGUN_RECIPIENT_OVERRIDE = recipient_override
    with pytest.raises(SendBatchException) as send_batch_exception:
        MailgunClient.send_batch(
            "email subject", "email body", recipient_tuples, chunk_size=chunk_size
        )

    if recipient_override is None:
        assert mock_post.call_count == 6
    else:
        assert mock_post.call_count == 1
        chunked_emails_to = [[(recipient_override, None)]]

    for call_num, args in enumerate(mock_post.call_args_list):
        called_args, called_kwargs = args
        assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
        assert called_kwargs["data"]["text"].startswith("email body")
        assert called_kwargs["data"]["subject"] == "email subject"
        assert sorted(called_kwargs["data"]["to"]) == sorted(
            [email for email, _ in chunked_emails_to[call_num]]
        )
        assert called_kwargs["data"]["recipient-variables"] == json.dumps(
            {email: context or {} for email, context in chunked_emails_to[call_num]}
        )

    exception_pairs = send_batch_exception.value.exception_pairs
    if recipient_override is None:
        assert len(exception_pairs) == 6
        for call_num, (recipients, exception) in enumerate(exception_pairs):
            assert sorted(recipients) == sorted(
                [email for email, _ in chunked_emails_to[call_num]]
            )
            assert isinstance(exception, HTTPError)
    else:
        assert len(exception_pairs) == 1
        assert exception_pairs[0][0] == [recipient_override]
        assert isinstance(exception_pairs[0][1], HTTPError)


def test_send_batch_400_no_raise(settings, mocker, mock_post, mocked_json):
    """
    Test that if raise_for_status is False we don't raise an exception for a 400 response
    """
    mock_post.return_value = mocker.Mock(
        spec=Response, status_code=HTTP_400_BAD_REQUEST, json=mocked_json()
    )

    chunk_size = 10
    recipient_tuples = [
        ("{0}@example.com".format(letter), None)  # noqa: UP030
        for letter in string.ascii_letters
    ]
    assert len(recipient_tuples) == 52
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    resp_list = MailgunClient.send_batch(
        "email subject",
        "email body",
        recipient_tuples,
        chunk_size=chunk_size,
        raise_for_status=False,
    )

    assert len(resp_list) == 6
    for resp in resp_list:
        assert resp.status_code == HTTP_400_BAD_REQUEST
    assert mock_post.call_count == 6
    assert mock_post.return_value.raise_for_status.called is False


def test_send_batch_exception(settings, mock_post):
    """
    Test that MailgunClient.send_batch returns a non-zero error code where the mailgun API returns a non-zero code
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    mock_post.side_effect = KeyError

    chunk_size = 10
    recipient_tuples = [
        ("{0}@example.com".format(letter), None)  # noqa: UP030
        for letter in string.ascii_letters
    ]
    chunked_emails_to = [
        recipient_tuples[i : i + chunk_size]
        for i in range(0, len(recipient_tuples), chunk_size)
    ]
    assert len(recipient_tuples) == 52
    with pytest.raises(SendBatchException) as send_batch_exception:
        MailgunClient.send_batch(
            "email subject", "email body", recipient_tuples, chunk_size=chunk_size
        )
    assert mock_post.called is True
    assert mock_post.call_count == 6
    for call_num, args in enumerate(mock_post.call_args_list):
        called_args, called_kwargs = args
        assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
        assert called_kwargs["data"]["text"].startswith("email body")
        assert called_kwargs["data"]["subject"] == "email subject"
        assert sorted(called_kwargs["data"]["to"]) == sorted(
            [email for email, _ in chunked_emails_to[call_num]]
        )
        assert called_kwargs["data"]["recipient-variables"] == json.dumps(
            {email: context or {} for email, context in chunked_emails_to[call_num]}
        )

    exception_pairs = send_batch_exception.value.exception_pairs
    assert len(exception_pairs) == 6
    for call_num, (recipients, exception) in enumerate(exception_pairs):
        assert sorted(recipients) == sorted(
            [email for email, _ in chunked_emails_to[call_num]]
        )
        assert isinstance(exception, KeyError)


def test_send_batch_improperly_configured(settings, mocker, mock_post):
    """
    If MailgunClient.send_batch returns a 401, it should raise a ImproperlyConfigured exception
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    mock_post.return_value = mocker.Mock(
        spec=Response, status_code=HTTP_401_UNAUTHORIZED
    )

    chunk_size = 10
    recipient_pairs = [
        ("{0}@example.com".format(letter), None)  # noqa: UP030
        for letter in string.ascii_letters
    ]
    with pytest.raises(ImproperlyConfigured) as ex:
        MailgunClient.send_batch(
            "email subject", "email body", recipient_pairs, chunk_size=chunk_size
        )
    assert ex.value.args[0] == "Mailgun API keys not properly configured."


def test_send_batch_empty(settings, mock_post):
    """If the recipient list is empty there should be no attempt to mail users"""
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    assert MailgunClient.send_batch("subject", "body", []) == []
    assert mock_post.called is False


@pytest.mark.parametrize("sender_name", [None, "Tester"])
def test_send_individual_email(settings, sender_name, mock_post):
    """
    Test that MailgunClient.send_individual_email() sends an individual message
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    context = {"abc": {"def": "xyz"}}
    response = MailgunClient.send_individual_email(
        subject="email subject",
        body="email body",
        recipient="a@example.com",
        recipient_variables=context,
        sender_name=sender_name,
    )
    assert response.status_code == HTTP_200_OK
    assert mock_post.called is True
    called_args, called_kwargs = mock_post.call_args
    assert list(called_args)[0] == "{}/{}".format(settings.MAILGUN_URL, "messages")  # noqa: RUF015
    assert called_kwargs["auth"] == ("api", settings.MAILGUN_KEY)
    assert called_kwargs["data"]["text"].startswith("email body")
    assert called_kwargs["data"]["subject"] == "email subject"
    assert called_kwargs["data"]["to"] == ["a@example.com"]
    assert called_kwargs["data"]["recipient-variables"] == json.dumps(
        {"a@example.com": context}
    )
    if sender_name is not None:
        assert called_kwargs["data"]["from"] == "{sender_name} <{email}>".format(
            sender_name=sender_name, email=settings.EMAIL_SUPPORT
        )
    else:
        assert called_kwargs["data"]["from"] == settings.EMAIL_SUPPORT


@pytest.mark.parametrize("raise_for_status", [True, False])
def test_send_individual_email_error(mocker, raise_for_status, mock_post, mocked_json):
    """
    Test handling of errors for send_individual_email
    """
    mock_post.return_value = mocker.Mock(
        spec=Response, status_code=HTTP_400_BAD_REQUEST, json=mocked_json
    )

    response = MailgunClient.send_individual_email(
        subject="email subject",
        body="email body",
        recipient="a@example.com",
        raise_for_status=raise_for_status,
    )

    assert response.raise_for_status.called is raise_for_status
    assert response.status_code == HTTP_400_BAD_REQUEST
    assert response.json() == {}


def test_send_with_sender_address(settings, mock_post):
    """
    Test that specifying a sender address in our mail API functions will result in an email
    with the sender address in the 'from' field
    """
    settings.MAILGUN_RECIPIENT_OVERRIDE = None
    sender_address = "sender@example.com"
    MailgunClient.send_batch(
        "email subject",
        "email body",
        batch_recipient_arg,
        sender_address=sender_address,
    )
    MailgunClient.send_individual_email(
        "email subject",
        "email body",
        individual_recipient_arg,
        sender_address=sender_address,
    )
    for args in mock_post.call_args_list:
        _, called_kwargs = args
        assert called_kwargs["data"]["from"] == sender_address
