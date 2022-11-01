"""
Tests for hubspot task_helpers
"""
import pytest

from applications.models import BootcampApplication
from ecommerce.models import Order
from hubspot.task_helpers import (
    sync_hubspot_application,
    sync_hubspot_application_from_order,
    sync_hubspot_user,
    sync_hubspot_product,
)
from klasses.factories import BootcampRunFactory

pytestmark = pytest.mark.django_db

# pylint:disable=redefined-outer-name


@pytest.fixture
def mock_hubspot(mocker):
    """Mock hubspot tasks"""
    return mocker.patch("hubspot.task_helpers.tasks", autospec=True)


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_application(settings, mock_hubspot, hubspot_key):
    """sync_hubspot_application task helper should call tasks if an API key is present"""
    settings.HUBSPOT_API_KEY = hubspot_key
    application = BootcampApplication()
    sync_hubspot_application(application)
    if hubspot_key is not None:
        mock_hubspot.sync_application_with_hubspot.delay.assert_called_once_with(
            application.id
        )
    else:
        mock_hubspot.sync_application_with_hubspot.delay.assert_not_called()


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_application_from_order(settings, mock_hubspot, hubspot_key):
    """sync_hubspot_application_from_order task helper should call tasks if an API key is present"""
    settings.HUBSPOT_API_KEY = hubspot_key
    order = Order(application=BootcampApplication())
    sync_hubspot_application_from_order(order)
    if hubspot_key is not None:
        mock_hubspot.sync_application_with_hubspot.delay.assert_called_once_with(
            order.application.id
        )
    else:
        mock_hubspot.sync_application_with_hubspot.delay.assert_not_called()


def test_sync_hubspot_application_from_order_no_application(settings, mocker):
    """sync_hubspot_application_from_order should log an error if no application exists for the order"""
    settings.HUBSPOT_API_KEY = "abc"
    mock_log = mocker.patch("hubspot.task_helpers.log.error")
    order = Order(application=None, id=2)
    sync_hubspot_application_from_order(order)
    mock_log.assert_called_once_with(
        "No matching BootcampApplication found for order %s", order.id
    )


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_user(settings, mock_hubspot, hubspot_key, user):
    """sync_hubspot_user helper should call task if an API key is present"""
    settings.HUBSPOT_API_KEY = hubspot_key
    sync_hubspot_user(user)
    if hubspot_key is not None:
        mock_hubspot.sync_contact_with_hubspot.delay.assert_called_once_with(user.id)
    else:
        mock_hubspot.sync_contact_with_hubspot.delay.assert_not_called()


@pytest.mark.parametrize("hubspot_key", [None, "abc"])
def test_sync_hubspot_product(settings, mock_hubspot, hubspot_key):
    """sync_hubspot_product helper should call task if an API key is present"""
    bootcamp_run = BootcampRunFactory.create()
    settings.HUBSPOT_API_KEY = hubspot_key
    sync_hubspot_product(bootcamp_run)
    if hubspot_key is not None:
        mock_hubspot.sync_product_with_hubspot.delay.assert_called_once_with(
            bootcamp_run.id
        )
    else:
        mock_hubspot.sync_product_with_hubspot.delay.assert_not_called()
