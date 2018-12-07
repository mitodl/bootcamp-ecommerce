"""
Tests for the bootcamp_admission_client module
"""
from urllib.parse import urljoin, urlencode

import pytest
from django.conf import settings
from rest_framework import status

from fluidreview.constants import WebhookParseStatus
from fluidreview.factories import WebhookRequestFactory
from klasses.bootcamp_admissions_client import (
    BootcampAdmissionClient,
    fetch_legacy_admissions,
)
from profiles.factories import ProfileFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db

JSON_RESP_OBJ = {
    "user": "foo@example.com",
    "bootcamps": [
        {
            "bootcamp_id": 1,
            "bootcamp_title": "Entrepreneurship",
            "klasses": [
                {
                    "klass_id": 13,
                    "klass_name": "Class 2 (Student)",
                    "status": "no_show",
                    "is_user_eligible_to_pay": False
                },
                {
                    "klass_id": 12,
                    "klass_name": "Class 1",
                    "status": "coming",
                    "is_user_eligible_to_pay": False
                }
            ]
        },
        {
            "bootcamp_id": 6,
            "bootcamp_title": "Master of Law",
            "klasses": [
                {
                    "klass_id": 16,
                    "klass_name": "Class 1",
                    "status": "scholarship_not_awarded",
                    "is_user_eligible_to_pay": True
                }
            ]
        },
        {
            "bootcamp_id": 8,
            "bootcamp_title": "Bootcamp title",
            "klasses": [
                {
                    "klass_id": 18,
                    "klass_name": "Class name",
                    "status": "coming",
                    "is_user_eligible_to_pay": True
                }
            ]
        }
    ]
}


@pytest.fixture()
def test_data(db):
    """
    Sets up the data for all the tests in this module
    """

    user_email = JSON_RESP_OBJ['user']
    url = "{base_url}?{params}".format(
        base_url=urljoin(settings.BOOTCAMP_ADMISSION_BASE_URL, '/api/v1/user/'),
        params=urlencode({
            'email': user_email,
            'key': settings.BOOTCAMP_ADMISSION_KEY,
        })
    )
    profile = ProfileFactory.create(user__email=user_email, fluidreview_id=9999, smapply_id=8888)
    payable_klass = 16
    unpayable_klass = 12
    sma_payable_class = 18
    return profile.user, url, payable_klass, unpayable_klass, sma_payable_class


@pytest.fixture()
def mocked_get_200(mocked_requests_get):
    """
    Mocked get with 200 response
    """
    mocked_requests_get.response.status_code = status.HTTP_200_OK
    mocked_requests_get.response.json.return_value = JSON_RESP_OBJ
    return mocked_requests_get


@pytest.fixture()
def mocked_get_400(mocked_requests_get):
    """
    Mocked get with 400 response
    """
    mocked_requests_get.response.status_code = status.HTTP_400_BAD_REQUEST
    mocked_requests_get.response.json.return_value = JSON_RESP_OBJ
    return mocked_requests_get


def test_happy_path(test_data, mocked_get_200):
    """
    Test BootcampAdmissionClient with a normal response
    """
    user, url, _, _, _ = test_data
    boot_client = BootcampAdmissionClient(user)
    mocked_get_200.request.assert_called_once_with(url)
    assert fetch_legacy_admissions(user) == JSON_RESP_OBJ
    assert boot_client.payable_klasses_keys == [
        JSON_RESP_OBJ['bootcamps'][1]['klasses'][0]['klass_id'],
        JSON_RESP_OBJ['bootcamps'][2]['klasses'][0]['klass_id']
    ]


def test_get_raises(test_data, mocked_get_200):
    """
    Test BootcampAdmissionClient in case the GET request to the service fails raising anything
    """
    user, url, _, _, _ = test_data
    mocked_get_200.request.side_effect = ZeroDivisionError

    boot_client = BootcampAdmissionClient(user)
    mocked_get_200.request.assert_called_once_with(url)
    assert boot_client.payable_klasses_keys == []


def test_status_code_not_200(test_data, mocked_get_400):
    """
    Test BootcampAdmissionClient in case the GET returns a status code different from 200
    """
    user, url, _, _, _ = test_data

    boot_client = BootcampAdmissionClient(user)
    mocked_get_400.request.assert_called_once_with(url)
    assert boot_client.payable_klasses_keys == []


def test_json_raises(test_data, mocked_get_200):
    """
    Test BootcampAdmissionClient in case the GET request to the service fails raising anything
    """
    user, url, _, _, _ = test_data

    mocked_get_200.response.json.side_effect = ZeroDivisionError

    boot_client = BootcampAdmissionClient(user)
    mocked_get_200.request.assert_called_once_with(url)
    assert boot_client.payable_klasses_keys == []


def test_can_pay_klass(test_data, mocked_get_200):
    """
    Test BootcampAdmissionClient.can_pay_klass with a mix of legacy and fluidreview klasses
    """
    user, _, payable_klass, unpayable_klass, sma_payable_klass = test_data
    fluidreview_klass = 19
    WebhookRequestFactory(
        award_id=fluidreview_klass,
        user_email=user.email,
        user_id=user.profile.fluidreview_id,
        status=WebhookParseStatus.SUCCEEDED)

    boot_client = BootcampAdmissionClient(user)
    assert boot_client.can_pay_klass(payable_klass) is True
    assert boot_client.can_pay_klass(unpayable_klass) is False
    assert boot_client.can_pay_klass(sma_payable_klass) is True
    assert boot_client.can_pay_klass(fluidreview_klass) is True
    assert boot_client.can_pay_klass('foo') is False


@pytest.mark.parametrize('status', [WebhookParseStatus.SUCCEEDED, WebhookParseStatus.FAILED])
def test_can_pay_klass_webhook_only(test_data, mocked_requests_get, status):
    """
    Test BootcampAdmissionClient.can_pay_klass when legacy admissions API is unavailable
    """
    mocked_requests_get.side_effect = ConnectionError
    user, _, payable_klass, _, _ = test_data
    fluidreview_klass = 19
    WebhookRequestFactory(
        award_id=fluidreview_klass,
        user_email=user.email,
        user_id=user.profile.fluidreview_id,
        status=status)

    boot_client = BootcampAdmissionClient(user)
    assert boot_client.can_pay_klass(payable_klass) is False
    assert boot_client.can_pay_klass(fluidreview_klass) is (status == WebhookParseStatus.SUCCEEDED)
