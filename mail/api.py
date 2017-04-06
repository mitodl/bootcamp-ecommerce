"""
Provides functions for sending and retrieving data about in-app email
"""
import logging
from itertools import islice
import json
import requests

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status

from mail.exceptions import SendBatchException


log = logging.getLogger(__name__)


class MailgunClient:
    """
    Provides functions for communicating with the Mailgun REST API.
    """
    _basic_auth_credentials = ('api', settings.MAILGUN_KEY)

    @staticmethod
    def default_params():
        """
        Default params for Mailgun request. This a method instead of an attribute to allow for the
        overriding of settings values.

        Returns:
            dict: A dict of default parameters for the Mailgun API
        """
        return {'from': settings.EMAIL_SUPPORT}

    @classmethod
    def _mailgun_request(  # pylint: disable=too-many-arguments
            cls, request_func, endpoint, params, sender_name=None, raise_for_status=True
    ):
        """
        Sends a request to the Mailgun API

        Args:
            request_func (function): requests library HTTP function (get/post/etc.)
            endpoint (str): Mailgun endpoint (eg: 'messages', 'events')
            params (dict): Dict of params to add to the request as 'data'
            raise_for_status (bool): If true, check the status and raise for non-2xx statuses
        Returns:
            requests.Response: HTTP response
        """
        mailgun_url = '{}/{}'.format(settings.MAILGUN_URL, endpoint)
        email_params = cls.default_params()
        email_params.update(params)
        # Update 'from' address if sender_name was specified
        if sender_name is not None:
            email_params['from'] = "{sender_name} <{email}>".format(
                sender_name=sender_name,
                email=email_params['from']
            )
        response = request_func(
            mailgun_url,
            auth=cls._basic_auth_credentials,
            data=email_params
        )
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Mailgun API keys not properly configured."
            log.error(message)
            raise ImproperlyConfigured(message)
        if raise_for_status:
            response.raise_for_status()
        return response

    @classmethod
    def _recipient_override(cls, body, recipients):
        """
        Helper method to override body and recipients of an email.
        If the MAILGUN_RECIPIENT_OVERRIDE setting is specified, the list of recipients
        will be ignored in favor of the recipients in that setting value.

        Args:
            body (str): Text email body
            recipients (list): A list of recipient emails
        Returns:
            tuple: A tuple of the (possibly) overridden recipients list and email body
        """
        if settings.MAILGUN_RECIPIENT_OVERRIDE is not None:
            body = '{0}\n\n[overridden recipient]\n{1}'.format(body, '\n'.join(recipients))
            recipients = [settings.MAILGUN_RECIPIENT_OVERRIDE]
        return body, recipients

    @classmethod
    def send_batch(cls, subject, body, recipients,  # pylint: disable=too-many-arguments, too-many-locals
                   sender_address=None, sender_name=None, chunk_size=settings.MAILGUN_BATCH_CHUNK_SIZE,
                   raise_for_status=True):
        """
        Sends a text email to a list of recipients (one email per recipient) via batch.

        Args:
            subject (str): Email subject
            body (str): Text email body
            recipients (iterable): A list of recipient emails
            sender_address (str): Sender email address
            sender_name (str): Sender name
            chunk_size (int): The maximum amount of emails to be sent at the same time
            raise_for_status (bool): If true, raise for non 2xx statuses

        Returns:
            list:
                List of responses which are HTTP responses from Mailgun.

        Raises:
            SendBatchException:
               If there is at least one exception, this exception is raised with all other exceptions in a list
               along with recipients we failed to send to.
        """
        original_recipients = recipients
        body, recipients = cls._recipient_override(body, original_recipients)
        responses = []
        exception_pairs = []

        recipients = iter(recipients)
        chunk = list(islice(recipients, chunk_size))
        while len(chunk) > 0:
            params = dict(
                to=chunk,
                subject=subject,
                text=body
            )
            params['recipient-variables'] = json.dumps({email: {} for email in chunk})
            if sender_address:
                params['from'] = sender_address

            if settings.MAILGUN_RECIPIENT_OVERRIDE is not None:
                original_recipients_chunk = original_recipients
            else:
                original_recipients_chunk = chunk

            try:
                response = cls._mailgun_request(
                    requests.post,
                    'messages',
                    params,
                    sender_name=sender_name,
                    raise_for_status=raise_for_status,
                )

                responses.append(response)
            except ImproperlyConfigured:
                raise
            except Exception as exception:  # pylint: disable=broad-except
                exception_pairs.append(
                    (original_recipients_chunk, exception)
                )
            chunk = list(islice(recipients, chunk_size))

        if len(exception_pairs) > 0:
            raise SendBatchException(exception_pairs)

        return responses

    @classmethod
    def send_individual_email(cls, subject, body, recipient,  # pylint: disable=too-many-arguments
                              sender_address=None, sender_name=None, raise_for_status=True):
        """
        Sends a text email to a single recipient.

        Args:
            subject (str): email subject
            body (str): email body
            recipient (str): email recipient
            sender_address (str): Sender email address
            sender_name (str): Sender name
            raise_for_status (bool): If true and a non-zero response was received,

        Returns:
            requests.Response: response from Mailgun
        """
        # Since .send_batch() returns a list, we need to return the first in the list
        responses = cls.send_batch(
            subject,
            body,
            [recipient],
            sender_address=sender_address,
            sender_name=sender_name,
            raise_for_status=raise_for_status,
        )
        return responses[0]
