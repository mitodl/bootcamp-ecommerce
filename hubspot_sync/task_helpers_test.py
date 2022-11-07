"""
Tests for hubspot_sync task_helpers
"""
import pytest

from applications.models import BootcampApplication
from ecommerce.models import Order
from hubspot_sync.task_helpers import (
    sync_hubspot_deal,
    sync_hubspot_deal_from_order,
    sync_hubspot_user,
    sync_hubspot_product,
)
from klasses.factories import BootcampRunFactory

pytestmark = pytest.mark.django_db

# pylint:disable=redefined-outer-name


@pytest.fixture
def mock_hubspot(mocker):
    """Mock hubspot_sync tasks"""
    return mocker.patch("hubspot_sync.task_helpers.tasks", autospec=True)


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_application(settings, mock_hubspot, hubspot_key):
    """ sync_hubspot_deal task helper should call tasks if an API key is present """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = hubspot_key
    application = BootcampApplication()
    sync_hubspot_deal(application)
    if hubspot_key is not None:
        mock_hubspot.sync_deal_with_hubspot.delay.assert_called_once_with(
            application.id
        )
    else:
        mock_hubspot.sync_deal_with_hubspot.delay.assert_not_called()


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_application_from_order(settings, mock_hubspot, hubspot_key):
    """ sync_hubspot_deal_from_order task helper should call tasks if an API key is present """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = hubspot_key
    order = Order(application=BootcampApplication())
    sync_hubspot_deal_from_order(order)
    if hubspot_key is not None:
        mock_hubspot.sync_deal_with_hubspot.delay.assert_called_once_with(
            order.application.id
        )
    else:
        mock_hubspot.sync_deal_with_hubspot.delay.assert_not_called()


def test_sync_hubspot_application_from_order_no_application(settings, mocker):
    """ sync_hubspot_deal_from_order should log an error if no application exists for the order """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = "abc"
    mock_log = mocker.patch("hubspot_sync.task_helpers.log.error")
    order = Order(application=None, id=2)
    sync_hubspot_deal_from_order(order)
    mock_log.assert_called_once_with(
        "No matching BootcampApplication found for order %s", order.id
    )


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_user(settings, mock_hubspot, hubspot_key, user):
    """ sync_hubspot_user helper should call task if an API key is present """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = hubspot_key
    sync_hubspot_user(user)
    if hubspot_key is not None:
        mock_hubspot.sync_contact_with_hubspot.delay.assert_called_once_with(user.id)
    else:
        mock_hubspot.sync_contact_with_hubspot.delay.assert_not_called()


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_product(settings, mock_hubspot, hubspot_key):
    """sync_hubspot_product helper should call task if an API key is present"""
    bootcamp_run = BootcampRunFactory.create()
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = hubspot_key
    sync_hubspot_product(bootcamp_run)
    if hubspot_key is not None:
        mock_hubspot.sync_product_with_hubspot.delay.assert_called_once_with(
            bootcamp_run.id
        )
    else:
        mock_hubspot.sync_product_with_hubspot.delay.assert_not_called()
