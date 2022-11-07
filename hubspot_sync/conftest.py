"""
Fixtures for hubspot_sync tests
"""
from datetime import datetime
from types import SimpleNamespace

import pytz
import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from hubspot.crm.objects import SimplePublicObject
from mitol.hubspot_api.factories import HubspotObjectFactory

from applications.models import BootcampApplication
from ecommerce.factories import OrderFactory
from klasses.factories import InstallmentFactory
from klasses.models import BootcampRun

# pylint: disable=redefined-outer-name

TIMESTAMPS = [
    datetime(2017, 1, 1, tzinfo=pytz.utc),
    datetime(2017, 1, 2, tzinfo=pytz.utc),
    datetime(2017, 1, 3, tzinfo=pytz.utc),
    datetime(2017, 1, 4, tzinfo=pytz.utc),
    datetime(2017, 1, 5, tzinfo=pytz.utc),
    datetime(2017, 1, 6, tzinfo=pytz.utc),
    datetime(2017, 1, 7, tzinfo=pytz.utc),
    datetime(2017, 1, 8, tzinfo=pytz.utc),
]

FAKE_OBJECT_ID = 1234
FAKE_HUBSPOT_ID = "1231213123"


@pytest.fixture
def mocked_celery(mocker):
    """Mock object that patches certain celery functions"""
    exception_class = TabError
    replace_mock = mocker.patch(
        "celery.app.task.Task.replace", autospec=True, side_effect=exception_class
    )
    group_mock = mocker.patch("celery.group", autospec=True)
    chain_mock = mocker.patch("celery.chain", autospec=True)

    yield SimpleNamespace(
        replace=replace_mock,
        group=group_mock,
        chain=chain_mock,
        replace_exception_class=exception_class,
    )


@pytest.fixture
def mock_logger(mocker):
    """ Mock the logger """
    yield mocker.patch("hubspot_sync.tasks.log.error")


@pytest.fixture
def mock_hubspot_request(mocker):
    """Mock the send hubspot_sync request method"""
    yield mocker.patch("hubspot_sync.tasks.send_hubspot_request")


@pytest.fixture
def mock_hubspot_api_request(mocker):
    """Mock the send hubspot_sync request method"""
    yield mocker.patch("hubspot_sync.api.send_hubspot_request")


@pytest.fixture
def hubspot_application():
    """ Return an order for testing with hubspot"""
    application = OrderFactory.create().application
    InstallmentFactory.create(bootcamp_run=application.bootcamp_run)

    HubspotObjectFactory.create(
        content_object=application.user,
        content_type=ContentType.objects.get_for_model(User),
        object_id=application.user.id,
    )
    HubspotObjectFactory.create(
        content_object=application.bootcamp_run,
        content_type=ContentType.objects.get_for_model(BootcampRun),
        object_id=application.bootcamp_run.id,
    )

    return application


@pytest.fixture
def hubspot_application_id(hubspot_application):
    """Create a HubspotObject for hubspot_application"""
    return HubspotObjectFactory.create(
        content_object=hubspot_application,
        content_type=ContentType.objects.get_for_model(BootcampApplication),
        object_id=hubspot_application.id,
    ).hubspot_id


@pytest.fixture
def mock_hubspot_api(mocker):
    """Mock the Hubspot CRM API"""
    mock_api = mocker.patch("mitol.hubspot_api.api.HubspotApi")
    mock_api.return_value.crm.objects.basic_api.create.return_value = (
        SimplePublicObject(id=FAKE_HUBSPOT_ID)
    )
    yield mock_api
