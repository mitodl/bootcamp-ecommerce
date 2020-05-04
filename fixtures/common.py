"""Common fixtures"""
# pylint: disable=unused-argument, redefined-outer-name

import pytest
import responses
from django.test.client import Client
from rest_framework.test import APIClient
from wagtail.core.models import Site

from profiles.factories import UserFactory


@pytest.fixture
def user(db):
    """Creates a user"""
    return UserFactory.create()


@pytest.fixture
def staff_user(db):
    """Staff user fixture"""
    return UserFactory.create(is_staff=True)


@pytest.fixture
def user_client(user):
    """Django test client that is authenticated with the user"""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def staff_client(staff_user):
    """Django test client that is authenticated with the staff user"""
    client = Client()
    client.force_login(staff_user)
    return client


@pytest.fixture
def user_drf_client(user):
    """DRF API test client that is authenticated with the user"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_drf_client(admin_user):
    """DRF API test client with admin user """
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def mocked_responses():
    """Mocked responses for requests library"""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def mock_context(mocker, user):
    """Mocked context for serializers"""
    return {"request": mocker.Mock(user=user)}


@pytest.fixture()
def wagtail_site():
    """Fixture for Wagtail default site"""
    return Site.objects.get(is_default_site=True)


@pytest.fixture()
def home_page(wagtail_site):
    """Fixture for the home page"""
    return wagtail_site.root_page
