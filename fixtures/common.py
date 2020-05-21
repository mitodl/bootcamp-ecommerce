"""Common fixtures"""
# pylint: disable=unused-argument, redefined-outer-name
from types import SimpleNamespace

import pytest
import responses

from django.test.client import Client
from rest_framework.test import APIClient
from wagtail.core.models import Site

from applications.constants import AppStates, VALID_SUBMISSION_TYPE_CHOICES
from applications.factories import BootcampApplicationFactory, ApplicationStepFactory, \
    BootcampRunApplicationStepFactory, ApplicationStepSubmissionFactory
from backends.edxorg import EdxOrgOAuth2
from klasses.factories import InstallmentFactory
from profiles.factories import UserFactory


@pytest.fixture
def social_extra_data():
    """Some fake data for populating social auth"""
    yield {
        "access_token": "fooooootoken",
        "refresh_token": "baaaarrefresh",
    }


@pytest.fixture
def user(db, social_extra_data):
    """Creates a user"""
    # create a user
    user = UserFactory.create()
    user.social_auth.create(
        provider='not_edx',
    )
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid="{}_edx".format(user.username),
        extra_data=social_extra_data
    )
    yield user


@pytest.fixture
def staff_user(db, user):
    """Staff user fixture"""
    user.is_staff = True
    user.save()


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


@pytest.fixture()
def awaiting_submission_app():
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_USER_SUBMISSIONS.value
    )
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)
    app_steps = [
        ApplicationStepFactory.create(
            submission_type=VALID_SUBMISSION_TYPE_CHOICES[0][0]
        ),
        ApplicationStepFactory.create(
            submission_type=VALID_SUBMISSION_TYPE_CHOICES[1][0]
        ),
    ]
    run_steps = [
        BootcampRunApplicationStepFactory.create(
            bootcamp_run=application.bootcamp_run, application_step=app_steps[0]
        ),
        BootcampRunApplicationStepFactory.create(
            bootcamp_run=application.bootcamp_run, application_step=app_steps[1]
        ),
    ]
    ApplicationStepSubmissionFactory.create(
        bootcamp_application=application, run_application_step=run_steps[0]
    )

    return SimpleNamespace(
        application=application,
        run_steps=run_steps,
        installment=installment
    )
