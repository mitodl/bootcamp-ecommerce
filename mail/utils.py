"""Mail utils"""

import requests
from requests.auth import HTTPBasicAuth

from django.conf import settings

from rest_framework import status


def validate_email_address_through_mailgun(email_id):
    """
    Validates email address through Mailgun API
    """
    if settings.MAILGUN_API_PUBLIC_KEY:
        basic_auth = HTTPBasicAuth("api", settings.MAILGUN_API_PUBLIC_KEY)
        payload = {"address": email_id}
        response = requests.get(
            "https://api.mailgun.net/v3/address/validate",
            params=payload,
            auth=basic_auth,
        )
        return response.status == status.HTTP_200_OK
    else:
        return False
