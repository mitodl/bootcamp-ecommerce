"""
APIs to access the remote bootcamp app that controls the admissions
"""
import logging
from urllib.parse import urljoin, urlencode

import requests
from django.conf import settings
from rest_framework import status

from klasses.tasks import async_cache_admissions


log = logging.getLogger(__name__)


class BootcampAdmissionClient:
    """
    Client for the bootcamp admission portal
    """

    admissions = {}
    payable_klasses = {}
    payable_klasses_keys = []

    def __init__(self, user_email):
        self.user_email = user_email
        self.admissions = self._get_admissions()
        self.payable_klasses = self._get_payable_klasses()
        self.payable_klasses_keys = list(self.payable_klasses.keys())
        # trigger the async task to cache the info
        if self.payable_klasses:
            async_cache_admissions.delay(self.user_email, self.payable_klasses)

    def _get_admissions(self):
        """
        Requests the bootcamp klasses where the user has been admitted.

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
                'email': self.user_email,
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
                self.user_email,
                resp.status_code,
            )
            return {}

        try:
            return resp.json()
        except:  # pylint: disable=bare-except
            log.exception('impossible to parse the JSON response')
            return {}

    def _get_payable_klasses(self):
        """
        Returns a list of the payable klasses.
        """
        adm_klasses = {}
        for bootcamp in self.admissions.get("bootcamps", []):
            for klass in bootcamp.get("klasses", []):
                if klass.get("is_user_eligible_to_pay") is True:
                    adm_klasses[klass["klass_id"]] = klass
        return adm_klasses

    def can_pay_klass(self, klass_key):
        """
        Whether the user can pay for a specific klass
        """
        return klass_key in self.payable_klasses_keys
