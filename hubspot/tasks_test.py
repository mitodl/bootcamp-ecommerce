"""
Tests for hubspot tasks
"""
# pylint: disable=redefined-outer-name
from unittest.mock import ANY, Mock

import pytest

from faker import Faker
from requests import HTTPError

from hubspot.api import (
    make_contact_sync_message,
    make_product_sync_message, make_deal_sync_message, make_line_sync_message)
from hubspot.conftest import TIMESTAMPS
from hubspot.factories import HubspotErrorCheckFactory
from hubspot.models import HubspotErrorCheck
from hubspot.tasks import (
    sync_contact_with_hubspot,
    HUBSPOT_SYNC_URL,
    check_hubspot_api_errors,
    sync_product_with_hubspot, sync_deal_with_hubspot, sync_line_with_hubspot, sync_bulk_with_hubspot)
from klasses.factories import BootcampFactory, PersonalPriceFactory
from profiles.factories import ProfileFactory
from smapply.api import SMApplyTaskCache

pytestmark = [pytest.mark.django_db]

fake = Faker()


@pytest.fixture
def mock_hubspot_request(mocker):
    """Mock the send hubspot request method"""
    yield mocker.patch("hubspot.tasks.send_hubspot_request", autospec=True)


def test_sync_contact_with_hubspot(mock_hubspot_request, user_data):
    """Test that send_hubspot_request is called properly for a CONTACT sync"""
    profile = ProfileFactory.create()
    profile.smapply_id = 102132
    profile.smapply_user_data = user_data
    profile.save()
    sync_contact_with_hubspot(profile.id)
    body = make_contact_sync_message(profile.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "CONTACT", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_product_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a PRODUCT sync"""
    bootcamp = BootcampFactory.create()
    sync_product_with_hubspot(bootcamp.id)
    body = make_product_sync_message(bootcamp.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "PRODUCT", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_deal_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a DEAL sync"""
    personal_price = PersonalPriceFactory.create(user__profile__smapply_id=102132)

    sync_deal_with_hubspot(personal_price.id)
    body = make_deal_sync_message(personal_price.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "DEAL", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_line_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a LINE sync"""
    personal_price = PersonalPriceFactory.create(user__profile__smapply_id=102132)

    sync_line_with_hubspot(personal_price.id)
    body = make_line_sync_message(personal_price.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "LINE_ITEM", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_errors_first_run(settings, mock_hubspot_errors, mock_logger):
    """Test that HubspotErrorCheck is created on 1st run and nothing is logged"""
    settings.HUBSPOT_API_KEY = "dkfjKJ2jfd"
    assert HubspotErrorCheck.objects.count() == 0
    check_hubspot_api_errors()
    assert HubspotErrorCheck.objects.count() == 1
    assert mock_hubspot_errors.call_count == 1
    assert mock_logger.call_count == 0


@pytest.mark.parametrize(
    "last_check_dt,expected_errors,call_count",
    [[TIMESTAMPS[0], 4, 3], [TIMESTAMPS[6], 1, 1]],
)
def test_sync_errors_new_errors(
    settings,
    mock_hubspot_errors,
    mock_logger,
    last_check_dt,
    expected_errors,
    call_count,
):  # pylint: disable=too-many-arguments
    """Test that errors more recent than last checked_on date are logged"""
    settings.HUBSPOT_API_KEY = "dkfjKJ2jfd"
    last_check = HubspotErrorCheckFactory.create(checked_on=last_check_dt)
    check_hubspot_api_errors()
    assert mock_hubspot_errors.call_count == call_count
    assert mock_logger.call_count == expected_errors
    assert HubspotErrorCheck.objects.first().checked_on > last_check.checked_on


def test_skip_error_checks(settings, mock_hubspot_errors):
    """Test that no requests to Hubspot are made if the HUBSPOT_API_KEY is not set """
    settings.HUBSPOT_API_KEY = None
    check_hubspot_api_errors()
    assert mock_hubspot_errors.call_count == 0


def test_sync_bulk(mocker):
    """Test the hubspot bulk sync function"""
    mock_request = mocker.patch('hubspot.tasks.send_hubspot_request')
    profile = ProfileFactory(smapply_user_data={'first_name': 'test', 'last_name': 'test', 'email': 'email'})
    task_cache = SMApplyTaskCache()
    sync_bulk_with_hubspot([profile], make_contact_sync_message, "CONTACT", task_cache=task_cache)
    mock_request.assert_called_once()


def test_sync_bulk_no_profiles(mocker):
    """Test the hubspot bulk sync function when no contacts have data to sync"""
    mock_request = mocker.patch('hubspot.tasks.send_hubspot_request')
    profile = ProfileFactory()
    task_cache = SMApplyTaskCache()
    sync_bulk_with_hubspot([profile], make_contact_sync_message, "CONTACT", task_cache=task_cache)
    mock_request.assert_not_called()


def test_sync_bulk_logs_errors(mocker):
    """Test that hubspot bulk sync correctly logs errors"""
    mock_request = mocker.patch(f"hubspot.api.requests.put", return_value=Mock(
        raise_for_status=Mock(side_effect=HTTPError())))
    mock_log = mocker.patch('hubspot.api.log.exception')

    profile = ProfileFactory(smapply_user_data={'first_name': 'test', 'last_name': 'test', 'email': 'email'})
    task_cache = SMApplyTaskCache()
    sync_bulk_with_hubspot([profile], make_contact_sync_message, "CONTACT", task_cache=task_cache)
    assert mock_request.call_count == 3
    mock_log.assert_called_once()
