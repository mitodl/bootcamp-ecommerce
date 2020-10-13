"""API functionality for integrating with NovoEd"""
from urllib.parse import urljoin
import logging
import operator

import requests
from django.conf import settings
from djangosaml2idp.processors import BaseProcessor
from rest_framework import status

from klasses.models import BootcampRunEnrollment
from main.utils import now_in_utc
from novoed.constants import (
    REGISTER_USER_URL_STUB,
    UNENROLL_USER_URL_STUB,
    SAML_ID_STAGING_PREFIX,
)
from profiles.api import get_first_and_last_names

log = logging.getLogger(__name__)


def enroll_in_novoed_course(user, novoed_course_stub):
    """
    Enrolls a user in a course on NovoEd

    Args:
        user (django.contrib.auth.models.User):
        novoed_course_stub (str): The stub of the course in NovoEd (can be found in the NovoEd course's URL)

    Returns:
        (bool, bool): A flag indicating whether or not the enrollment succeeded, paired with a flag indicating
            whether or not the enrollment already existed

    Raises:
        HTTPError: Raised if the HTTP response indicates an error
    """
    first_name, last_name = get_first_and_last_names(user)
    new_user_req_body = {
        "api_key": settings.NOVOED_API_KEY,
        "api_secret": settings.NOVOED_API_SECRET,
        "catalog_id": novoed_course_stub,
        "first_name": first_name,
        "last_name": last_name,
        "email": user.email,
        "external_id": str(user.id),
    }
    new_user_url = urljoin(
        settings.NOVOED_API_BASE_URL, f"{novoed_course_stub}/{REGISTER_USER_URL_STUB}"
    )
    resp = requests.post(new_user_url, json=new_user_req_body)
    created, existed = False, False
    if resp.status_code == status.HTTP_200_OK:
        BootcampRunEnrollment.objects.filter(
            user=user, bootcamp_run__novoed_course_stub=novoed_course_stub
        ).update(novoed_sync_date=now_in_utc())
        created = True
    elif resp.status_code == status.HTTP_207_MULTI_STATUS:
        existed = True
    elif resp.ok:
        log.error(
            "Received an unexpected response from NovoEd when enrolling (%s, %s)",
            user.email,
            novoed_course_stub,
        )
    else:
        resp.raise_for_status()
    return created, existed


def unenroll_from_novoed_course(user, novoed_course_stub):
    """
    Enrolls a user from a course on NovoEd

    Args:
        user (django.contrib.auth.models.User):
        novoed_course_stub (str): The stub of the course in NovoEd (can be found in the NovoEd course's URL)

    Raises:
        HTTPError: Raised if the HTTP response indicates an error
    """
    unenroll_user_req_body = {
        "api_key": settings.NOVOED_API_KEY,
        "api_secret": settings.NOVOED_API_SECRET,
        "email": user.email,
    }
    unenroll_user_url = urljoin(
        settings.NOVOED_API_BASE_URL, f"{novoed_course_stub}/{UNENROLL_USER_URL_STUB}"
    )
    resp = requests.post(unenroll_user_url, json=unenroll_user_req_body)
    resp.raise_for_status()


class NovoEdSamlProcessor(BaseProcessor):
    """
    SAML request processor that overrides the default to allow for specialized functionality
    when responding to auth requests.
    """

    def create_identity(self, user, sp_attribute_mapping):
        results = {}
        for user_attr, out_attr in sp_attribute_mapping.items():
            # This line allows the attribute map for a ServiceProvider record to have keys that refer to
            # an object path (e.g.: "profile.name") rather than just a property name
            attr = operator.attrgetter(user_attr)(user)
            if attr is not None:
                attr_value = attr() if callable(attr) else attr
                if user_attr == "id" and settings.ENVIRONMENT not in {
                    "prod",
                    "production",
                }:
                    attr_value = "".join([SAML_ID_STAGING_PREFIX, str(attr_value)])
                results[out_attr] = attr_value
        return results
