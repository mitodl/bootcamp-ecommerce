"""
APIs to access the remote bootcamp app that controls the admissions
"""
import logging
from urllib.parse import urljoin, urlencode

import requests
from django.conf import settings
from rest_framework import status

from fluidreview.constants import WebhookParseStatus
from fluidreview.models import WebhookRequest

log = logging.getLogger(__name__)


def fetch_legacy_admissions(user_email):
    """
    Requests the bootcamp klasses where the user has been admitted.

    Args:
        user_email (str): A user's email address

    Returns:
        dict:
            This should return a response like:
            {
                "user":"foo@example.com",
                "bootcamps":[
                    {
                        "bootcamp_id":6,
                        "bootcamp_title":"Master of Law",
                        "klasses":[
                            {
                                "klass_id":13,
                                "klass_name":"Class 2 (Student)",
                                "status":"no_show",
                                "is_user_eligible_to_pay":false
                            },
                            {
                                "klass_id":16,
                                "klass_name":"Class 1",
                                "status":"scholarship_not_awarded",
                                "is_user_eligible_to_pay":true
                            }
                        ]
                    }
                ]
            }
    """
    url = "{base_url}?{params}".format(
        base_url=urljoin(settings.BOOTCAMP_ADMISSION_BASE_URL, '/api/v1/user/'),
        params=urlencode({
            'email': user_email,
            'key': settings.BOOTCAMP_ADMISSION_KEY,
        })
    )

    try:
        resp = requests.get(url)
    except:  # pylint: disable=bare-except
        log.exception('request to bootcamp admission service failed')
        # in case of errors return an empty response
        return {}

    if resp.status_code != status.HTTP_200_OK:
        log.error(
            'request to bootcamp admission service for user %s returned unexpected code %s',
            user_email,
            resp.status_code,
        )
        return {}

    try:
        return resp.json()
    except:  # pylint: disable=bare-except
        log.exception('impossible to parse the JSON response')
        return {}


def fetch_fluidreview_klass_keys(fluid_user_id):
    """
    Collect all the unique award ids (== klass ids) from WebhookRequests by user email

    Args:
        fluid_user_id(int): FluidReview id for a user

    Returns:
        list: FluidReview award_ids for a user
    """
    return list(
        WebhookRequest.objects.filter(
            user_id=fluid_user_id,
            status=WebhookParseStatus.SUCCEEDED
        ).distinct('award_id').values_list('award_id', flat=True)
    )


def get_legacy_payable_klass_ids(admissions):
    """
    Returns a list of the payable klass ids.

    Args:
        admissions (dict): The legacy
    """
    adm_klasses = []
    for bootcamp in admissions.get("bootcamps", []):
        for klass in bootcamp.get("klasses", []):
            if klass.get("is_user_eligible_to_pay") is True:
                adm_klasses.append(klass['klass_id'])
    return adm_klasses


class BootcampAdmissionClient:
    """
    Client for the bootcamp admission portal
    """

    def __init__(self, user):
        """
        Fetch information about a user's admissions for the bootcamp

        Args:
            user (User): A user
        """
        legacy_admissions = fetch_legacy_admissions(user.email)
        self._klass_keys = get_legacy_payable_klass_ids(legacy_admissions) + \
            fetch_fluidreview_klass_keys(user.profile.fluidreview_id)

    @property
    def payable_klasses_keys(self):
        """
        A list of klass keys which the user can pay for
        """
        return self._klass_keys

    def can_pay_klass(self, klass_key):
        """
        Whether the user can pay for a specific klass
        """
        return klass_key in self.payable_klasses_keys
