"""
Provides functions for sending and retrieving data about in-app email
"""
import logging
import json

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import status

from main.utils import chunks
from mail.exceptions import SendBatchException


log = logging.getLogger(__name__)


class MailgunClient:
    """
    Provides functions for communicating with the Mailgun REST API.
    """

    _basic_auth_credentials = ("api", settings.MAILGUN_KEY)

    @staticmethod
    def default_params():
        """
        Default params for Mailgun request. This a method instead of an attribute to allow for the
        overriding of settings values.

        Returns:
            dict: A dict of default parameters for the Mailgun API
        """
        return {"from": settings.EMAIL_SUPPORT}

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
        mailgun_url = "{}/{}".format(settings.MAILGUN_URL, endpoint)
        email_params = cls.default_params()
        email_params.update(params)
        # Update 'from' address if sender_name was specified
        if sender_name is not None:
            email_params["from"] = "{sender_name} <{email}>".format(
                sender_name=sender_name, email=email_params["from"]
            )
        response = request_func(
            mailgun_url, auth=cls._basic_auth_credentials, data=email_params
        )
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Mailgun API keys not properly configured."
            log.error(message)
            raise ImproperlyConfigured(message)
        if raise_for_status:
            response.raise_for_status()
        return response

    @classmethod
    def send_batch(
        cls,
        subject,
        body,
        recipients,  # pylint: disable=too-many-arguments, too-many-locals
        sender_address=None,
        sender_name=None,
        chunk_size=settings.MAILGUN_BATCH_CHUNK_SIZE,
        raise_for_status=True,
    ):  # pylint:disable=too-many-locals, too-many-arguments
        """
        Sends a text email to a list of recipients (one email per recipient) via batch.

        Args:
            subject (str): Email subject
            body (str): Text email body
            recipients (iterable of (recipient, context)):
                A list where each tuple is:
                    (recipient, context)
                Where the recipient is an email address and context is a dict of variables for templating
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
        # Convert null contexts to empty dicts
        recipients = ((email, context or {}) for email, context in recipients)

        if settings.MAILGUN_RECIPIENT_OVERRIDE is not None:
            # This is used for debugging only
            body = "{body}\n\n[overridden recipient]\n{recipient_data}".format(
                body=body,
                recipient_data="\n".join(
                    [
                        "{}: {}".format(recipient, json.dumps(context))
                        for recipient, context in recipients
                    ]
                ),
            )
            recipients = [(settings.MAILGUN_RECIPIENT_OVERRIDE, {})]

        responses = []
        exception_pairs = []

        for chunk in chunks(recipients, chunk_size=chunk_size):
            chunk_dict = {email: context for email, context in chunk}
            emails = list(chunk_dict.keys())

            params = {
                "to": emails,
                "subject": subject,
                "text": body,
                "recipient-variables": json.dumps(chunk_dict),
            }
            if sender_address:
                params["from"] = sender_address

            try:
                response = cls._mailgun_request(
                    requests.post,
                    "messages",
                    params,
                    sender_name=sender_name,
                    raise_for_status=raise_for_status,
                )

                responses.append(response)
            except ImproperlyConfigured:
                raise
            except Exception as exception:  # pylint: disable=broad-except
                exception_pairs.append((emails, exception))

        if len(exception_pairs) > 0:
            raise SendBatchException(exception_pairs)

        return responses

    @classmethod
    def send_individual_email(
        cls,
        subject,
        body,
        recipient,  # pylint: disable=too-many-arguments
        recipient_variables=None,
        sender_address=None,
        sender_name=None,
        raise_for_status=True,
    ):  # pylint:disable=too-many-arguments
        """
        Sends a text email to a single recipient.

        Args:
            subject (str): email subject
            body (str): email body
            recipient (str): email recipient
            recipient_variables (dict): A dict of template variables to use (may be None for empty)
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
            [(recipient, recipient_variables)],
            sender_address=sender_address,
            sender_name=sender_name,
            raise_for_status=raise_for_status,
        )
        return responses[0]
