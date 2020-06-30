"""
Tests for hubspot tasks
"""
# pylint: disable=redefined-outer-name
from unittest.mock import ANY, Mock

import pytest

from faker import Faker
from requests import HTTPError

from applications.factories import BootcampApplicationFactory
from hubspot.api import (
    make_contact_sync_message,
    make_product_sync_message,
    make_deal_sync_message,
    make_line_sync_message,
)
from hubspot.conftest import TIMESTAMPS, FAKE_OBJECT_ID
from hubspot.factories import HubspotErrorCheckFactory, HubspotLineResyncFactory
from hubspot.models import HubspotErrorCheck, HubspotLineResync
from hubspot.tasks import (
    sync_contact_with_hubspot,
    HUBSPOT_SYNC_URL,
    check_hubspot_api_errors,
    sync_product_with_hubspot,
    sync_deal_with_hubspot,
    sync_line_with_hubspot,
    sync_bulk_with_hubspot,
    sync_application_with_hubspot,
    retry_invalid_line_associations,
)
from klasses.factories import InstallmentFactory, BootcampRunFactory
from profiles.factories import ProfileFactory, UserFactory

pytestmark = [pytest.mark.django_db]

fake = Faker()


@pytest.fixture
def mock_hubspot_request(mocker):
    """Mock the send hubspot request method"""
    yield mocker.patch("hubspot.tasks.send_hubspot_request", autospec=True)


def test_sync_contact_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a CONTACT sync"""
    profile = ProfileFactory.create()
    sync_contact_with_hubspot(profile.user.id)
    body = make_contact_sync_message(profile.user.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "CONTACT", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_contact_with_hubspot_missing_email(mock_hubspot_request):
    """Test that send_hubspot_request is not called if email is not in message"""
    user = UserFactory.create(profile=None)
    sync_contact_with_hubspot(user.id)
    mock_hubspot_request.assert_not_called()


def test_sync_product_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a PRODUCT sync"""
    bootcamp_run = BootcampRunFactory.create()
    sync_product_with_hubspot(bootcamp_run.id)
    body = make_product_sync_message(bootcamp_run.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "PRODUCT", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_application_with_hubspot(mocker):
    """Test that both sync_deal and sync_line tasks are called from sync_application"""
    mock_deal_sync = mocker.patch("hubspot.tasks.sync_deal_with_hubspot.si")
    mock_line_sync = mocker.patch("hubspot.tasks.sync_line_with_hubspot.si")
    application = BootcampApplicationFactory.create()
    InstallmentFactory.create(bootcamp_run=application.bootcamp_run)
    sync_application_with_hubspot(application.id)
    mock_deal_sync.assert_called_once_with(application.id)
    mock_line_sync.assert_called_once_with(application.id)


def test_sync_deal_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a DEAL sync"""
    application = BootcampApplicationFactory.create()
    InstallmentFactory.create(bootcamp_run=application.bootcamp_run)

    sync_deal_with_hubspot(application.id)
    body = make_deal_sync_message(application.id)
    body[0]["changeOccurredTimestamp"] = ANY
    mock_hubspot_request.assert_called_once_with(
        "DEAL", HUBSPOT_SYNC_URL, "PUT", body=body
    )


def test_sync_line_with_hubspot(mock_hubspot_request):
    """Test that send_hubspot_request is called properly for a LINE sync"""
    application = BootcampApplicationFactory.create()
    sync_line_with_hubspot(application.id)
    body = make_line_sync_message(application.id)
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
    "last_check_dt,expected_errors,call_count,application_exists",
    [
        [TIMESTAMPS[0], 4, 3, True],
        [TIMESTAMPS[0], 5, 3, False],
        [TIMESTAMPS[6], 1, 1, False],
    ],
)
def test_sync_errors_new_errors(
    settings,
    mocker,
    mock_hubspot_errors,
    mock_logger,
    last_check_dt,
    expected_errors,
    call_count,
    application_exists,
):  # pylint: disable=too-many-arguments
    """Test that errors more recent than last checked_on date are logged"""
    mock_retry = mocker.patch("hubspot.tasks.retry_invalid_line_associations")
    last_check = HubspotErrorCheckFactory.create(checked_on=last_check_dt)
    if application_exists:
        BootcampApplicationFactory.create(id=FAKE_OBJECT_ID)
    settings.HUBSPOT_API_KEY = "dkfjKJ2jfd"
    check_hubspot_api_errors()
    assert mock_hubspot_errors.call_count == call_count
    assert mock_logger.call_count == expected_errors
    assert HubspotErrorCheck.objects.first().checked_on > last_check.checked_on
    assert HubspotLineResync.objects.count() == (1 if application_exists else 0)
    assert mock_retry.call_count == 1


@pytest.mark.parametrize("deal_exists", [True, False])
@pytest.mark.parametrize("line_exists", [True, False])
def test_retry_invalid_line_associations(mocker, deal_exists, line_exists):
    """
    Test that a HubspotLineResync is deleted if the line exists on Hubspot,
    and sync_line_with_hubspot otherwise if the deal is on hubspot
    """
    mock_line_task = mocker.patch("hubspot.tasks.sync_line_with_hubspot")
    mock_application_task = mocker.patch("hubspot.tasks.sync_application_with_hubspot")
    mock_exists = mocker.patch(
        "hubspot.tasks.exists_in_hubspot", side_effect=[line_exists, deal_exists]
    )
    resync = HubspotLineResyncFactory.create()
    retry_invalid_line_associations()
    mock_exists.assert_any_call("LINE_ITEM", resync.application.integration_id)
    if not line_exists:
        mock_exists.assert_any_call("DEAL", resync.application.integration_id)
    assert HubspotLineResync.objects.filter(application=resync.application).count() == (
        1 if not line_exists else 0
    )
    assert mock_line_task.call_count == (1 if (deal_exists and not line_exists) else 0)
    assert mock_application_task.call_count == (
        1 if (not line_exists and not deal_exists) else 0
    )


def test_skip_error_checks(settings, mock_hubspot_errors):
    """Test that no requests to Hubspot are made if the HUBSPOT_API_KEY is not set """
    settings.HUBSPOT_API_KEY = None
    check_hubspot_api_errors()
    assert mock_hubspot_errors.call_count == 0


def test_sync_bulk(mocker):
    """Test the hubspot bulk sync function"""
    mock_request = mocker.patch("hubspot.tasks.send_hubspot_request")
    profile = ProfileFactory.create()
    sync_bulk_with_hubspot([profile.user], make_contact_sync_message, "CONTACT")
    mock_request.assert_called_once()


def test_sync_bulk_logs_errors(mocker):
    """Test that hubspot bulk sync correctly logs errors"""
    mock_request = mocker.patch(
        f"hubspot.api.requests.put",
        return_value=Mock(raise_for_status=Mock(side_effect=HTTPError())),
    )
    mock_log = mocker.patch("hubspot.tasks.log.exception")

    profile = ProfileFactory.create()
    sync_bulk_with_hubspot([profile.user], make_contact_sync_message, "CONTACT")
    assert mock_request.call_count == 3
    mock_log.assert_called_once()
