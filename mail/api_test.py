"""
Test cases for email API
"""
import json
import string
from unittest.mock import Mock, patch

from ddt import ddt, data
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import (
    override_settings,
    TestCase,
)
from requests import Response
from requests.exceptions import HTTPError
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from mail.exceptions import SendBatchException
from mail.api import MailgunClient


def mocked_json(return_data=None):
    """Mocked version of the json method for the Response class"""
    if return_data is None:
        return_data = {}

    def json(*args, **kwargs):  # pylint:disable=unused-argument, missing-docstring, redefined-outer-name
        return return_data
    return json


@ddt
@patch('requests.post', autospec=True, return_value=Mock(
    spec=Response,
    status_code=HTTP_200_OK,
    json=mocked_json()
))
class MailAPITests(TestCase):
    """
    Tests for the Mailgun client class
    """
    batch_recipient_arg = [('a@example.com', None), ('b@example.com', {"name": "B"})]
    individual_recipient_arg = 'a@example.com'

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    @data(None, 'Tester')
    def test_send_batch(self, sender_name, mock_post):
        """
        Test that MailgunClient.send_batch sends expected parameters to the Mailgun API
        Base case with only one batch call to the Mailgun API.
        """
        MailgunClient.send_batch('email subject', 'email body', self.batch_recipient_arg, sender_name=sender_name)
        assert mock_post.called
        called_args, called_kwargs = mock_post.call_args
        assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
        assert called_kwargs['auth'] == ('api', settings.MAILGUN_KEY)
        assert called_kwargs['data']['text'].startswith('email body')
        assert called_kwargs['data']['subject'] == 'email subject'
        assert sorted(called_kwargs['data']['to']) == sorted([email for email, _ in self.batch_recipient_arg])
        assert called_kwargs['data']['recipient-variables'] == json.dumps(
            {
                'a@example.com': {},
                'b@example.com': {'name': 'B'},
            }
        )
        if sender_name is not None:
            self.assertEqual(
                called_kwargs['data']['from'],
                "{sender_name} <{email}>".format(sender_name=sender_name, email=settings.EMAIL_SUPPORT)
            )
        else:
            self.assertEqual(called_kwargs['data']['from'], settings.EMAIL_SUPPORT)

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE='recipient@override.com')
    def test_send_batch_recipient_override(self, mock_post):
        """
        Test that MailgunClient.send_batch works properly with recipient override enabled
        """
        MailgunClient.send_batch('subject', 'body', self.batch_recipient_arg, sender_name='sender')
        assert mock_post.called
        called_args, called_kwargs = mock_post.call_args
        assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
        assert called_kwargs['auth'] == ('api', settings.MAILGUN_KEY)
        assert called_kwargs['data']['text'] == """body

[overridden recipient]
a@example.com: {}
b@example.com: {"name": "B"}"""
        assert called_kwargs['data']['subject'] == 'subject'
        assert called_kwargs['data']['to'] == ['recipient@override.com']
        assert called_kwargs['data']['recipient-variables'] == json.dumps(
            {
                'recipient@override.com': {},
            }
        )
        self.assertEqual(called_kwargs['data']['from'], "sender <support@example.com>")

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    def test_send_batch_chunk(self, mock_post):
        """
        Test that MailgunClient.send_batch chunks recipients
        """
        chunk_size = 10
        recipient_tuples = [("{0}@example.com".format(letter), None) for letter in string.ascii_letters]
        chunked_emails_to = [recipient_tuples[i:i + chunk_size] for i in range(0, len(recipient_tuples), chunk_size)]
        assert len(recipient_tuples) == 52
        responses = MailgunClient.send_batch('email subject', 'email body', recipient_tuples, chunk_size=chunk_size)
        assert mock_post.called
        assert mock_post.call_count == 6
        for call_num, args in enumerate(mock_post.call_args_list):
            called_args, called_kwargs = args
            assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
            assert called_kwargs['data']['text'].startswith('email body')
            assert called_kwargs['data']['subject'] == 'email subject'
            assert sorted(called_kwargs['data']['to']) == sorted([email for email, _ in chunked_emails_to[call_num]])
            assert called_kwargs['data']['recipient-variables'] == json.dumps(
                {email: context or {} for email, context in chunked_emails_to[call_num]}
            )

            response = responses[call_num]
            assert response.status_code == HTTP_200_OK

    @data(None, 'recipient_override@example.com')
    def test_send_batch_error(self, recipient_override, mock_post):
        """
        Test that MailgunClient.send_batch returns a non-zero error code where the mailgun API returns a non-zero code
        """
        mock_post.return_value = Response()
        mock_post.return_value.status_code = HTTP_400_BAD_REQUEST

        chunk_size = 10
        recipient_tuples = [("{0}@example.com".format(letter), {"letter": letter}) for letter in string.ascii_letters]
        chunked_emails_to = [recipient_tuples[i:i + chunk_size] for i in range(0, len(recipient_tuples), chunk_size)]
        assert len(recipient_tuples) == 52
        with override_settings(
            MAILGUN_RECIPIENT_OVERRIDE=recipient_override,
        ), self.assertRaises(SendBatchException) as send_batch_exception:
            MailgunClient.send_batch('email subject', 'email body', recipient_tuples, chunk_size=chunk_size)

        if recipient_override is None:
            assert mock_post.call_count == 6
        else:
            assert mock_post.call_count == 1
            chunked_emails_to = [[(recipient_override, None)]]

        for call_num, args in enumerate(mock_post.call_args_list):
            called_args, called_kwargs = args
            assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
            assert called_kwargs['data']['text'].startswith('email body')
            assert called_kwargs['data']['subject'] == 'email subject'
            assert sorted(called_kwargs['data']['to']) == sorted([email for email, _ in chunked_emails_to[call_num]])
            assert called_kwargs['data']['recipient-variables'] == json.dumps(
                {email: context or {} for email, context in chunked_emails_to[call_num]}
            )

        exception_pairs = send_batch_exception.exception.exception_pairs
        if recipient_override is None:
            assert len(exception_pairs) == 6
            for call_num, (recipients, exception) in enumerate(exception_pairs):
                assert sorted(recipients) == sorted([email for email, _ in chunked_emails_to[call_num]])
                assert isinstance(exception, HTTPError)
        else:
            assert len(exception_pairs) == 1
            assert exception_pairs[0][0] == [recipient_override]
            assert isinstance(exception_pairs[0][1], HTTPError)

    def test_send_batch_400_no_raise(self, mock_post):
        """
        Test that if raise_for_status is False we don't raise an exception for a 400 response
        """
        mock_post.return_value = Mock(
            spec=Response,
            status_code=HTTP_400_BAD_REQUEST,
            json=mocked_json()
        )

        chunk_size = 10
        recipient_tuples = [("{0}@example.com".format(letter), None) for letter in string.ascii_letters]
        assert len(recipient_tuples) == 52
        with override_settings(
            MAILGUN_RECIPIENT_OVERRIDE=None,
        ):
            resp_list = MailgunClient.send_batch(
                'email subject', 'email body', recipient_tuples, chunk_size=chunk_size, raise_for_status=False
            )

        assert len(resp_list) == 6
        for resp in resp_list:
            assert resp.status_code == HTTP_400_BAD_REQUEST
        assert mock_post.call_count == 6
        assert mock_post.return_value.raise_for_status.called is False

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    def test_send_batch_exception(self, mock_post):
        """
        Test that MailgunClient.send_batch returns a non-zero error code where the mailgun API returns a non-zero code
        """
        mock_post.side_effect = KeyError

        chunk_size = 10
        recipient_tuples = [("{0}@example.com".format(letter), None) for letter in string.ascii_letters]
        chunked_emails_to = [recipient_tuples[i:i + chunk_size] for i in range(0, len(recipient_tuples), chunk_size)]
        assert len(recipient_tuples) == 52
        with self.assertRaises(SendBatchException) as send_batch_exception:
            MailgunClient.send_batch('email subject', 'email body', recipient_tuples, chunk_size=chunk_size)
        assert mock_post.called
        assert mock_post.call_count == 6
        for call_num, args in enumerate(mock_post.call_args_list):
            called_args, called_kwargs = args
            assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
            assert called_kwargs['data']['text'].startswith('email body')
            assert called_kwargs['data']['subject'] == 'email subject'
            assert sorted(called_kwargs['data']['to']) == sorted([email for email, _ in chunked_emails_to[call_num]])
            assert called_kwargs['data']['recipient-variables'] == json.dumps(
                {email: context or {} for email, context in chunked_emails_to[call_num]}
            )

        exception_pairs = send_batch_exception.exception.exception_pairs
        assert len(exception_pairs) == 6
        for call_num, (recipients, exception) in enumerate(exception_pairs):
            assert sorted(recipients) == sorted([email for email, _ in chunked_emails_to[call_num]])
            assert isinstance(exception, KeyError)

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    def test_send_batch_improperly_configured(self, mock_post):
        """
        If MailgunClient.send_batch returns a 401, it should raise a ImproperlyConfigured exception
        """
        mock_post.return_value = Mock(
            spec=Response,
            status_code=HTTP_401_UNAUTHORIZED,
        )

        chunk_size = 10
        recipient_pairs = [("{0}@example.com".format(letter), None) for letter in string.ascii_letters]
        with self.assertRaises(ImproperlyConfigured) as ex:
            MailgunClient.send_batch('email subject', 'email body', recipient_pairs, chunk_size=chunk_size)
        assert ex.exception.args[0] == "Mailgun API keys not properly configured."

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    def test_send_batch_empty(self, mock_post):
        """If the recipient list is empty there should be no attempt to mail users"""
        assert MailgunClient.send_batch('subject', 'body', []) == []
        assert mock_post.called is False

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    @data(None, 'Tester')
    def test_send_individual_email(self, sender_name, mock_post):
        """
        Test that MailgunClient.send_individual_email() sends an individual message
        """
        context = {'abc': {'def': 'xyz'}}
        response = MailgunClient.send_individual_email(
            subject='email subject',
            body='email body',
            recipient='a@example.com',
            recipient_variables=context,
            sender_name=sender_name,
        )
        assert response.status_code == HTTP_200_OK
        assert mock_post.called
        called_args, called_kwargs = mock_post.call_args
        assert list(called_args)[0] == '{}/{}'.format(settings.MAILGUN_URL, 'messages')
        assert called_kwargs['auth'] == ('api', settings.MAILGUN_KEY)
        assert called_kwargs['data']['text'].startswith('email body')
        assert called_kwargs['data']['subject'] == 'email subject'
        assert called_kwargs['data']['to'] == ['a@example.com']
        assert called_kwargs['data']['recipient-variables'] == json.dumps({'a@example.com': context})
        if sender_name is not None:
            self.assertEqual(
                called_kwargs['data']['from'],
                "{sender_name} <{email}>".format(sender_name=sender_name, email=settings.EMAIL_SUPPORT)
            )
        else:
            self.assertEqual(called_kwargs['data']['from'], settings.EMAIL_SUPPORT)

    @data(True, False)
    def test_send_individual_email_error(self, raise_for_status, mock_post):
        """
        Test handling of errors for send_individual_email
        """
        mock_post.return_value = Mock(
            spec=Response,
            status_code=HTTP_400_BAD_REQUEST,
            json=mocked_json()
        )

        response = MailgunClient.send_individual_email(
            subject='email subject',
            body='email body',
            recipient='a@example.com',
            raise_for_status=raise_for_status,
        )

        assert response.raise_for_status.called is raise_for_status
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.json() == {}

    @override_settings(MAILGUN_RECIPIENT_OVERRIDE=None)
    def test_send_with_sender_address(self, mock_post):
        """
        Test that specifying a sender address in our mail API functions will result in an email
        with the sender address in the 'from' field
        """
        sender_address = 'sender@example.com'
        MailgunClient.send_batch(
            'email subject', 'email body', self.batch_recipient_arg, sender_address=sender_address
        )
        MailgunClient.send_individual_email(
            'email subject', 'email body', self.individual_recipient_arg, sender_address=sender_address
        )
        for args in mock_post.call_args_list:
            _, called_kwargs = args
            assert called_kwargs['data']['from'] == sender_address
