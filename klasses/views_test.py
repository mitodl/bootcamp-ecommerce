"""Views for bootcamps"""
from collections import namedtuple
from datetime import timedelta

from django.urls import reverse
import pytest
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from applications.factories import BootcampApplicationFactory
from klasses.factories import BootcampRunFactory
from klasses.serializers import BootcampRunSerializer
from main.utils import now_in_utc


pytestmark = pytest.mark.django_db


RunInfo = namedtuple(
    "RunInfo", ["available_run", "unavailable_run", "submitted_application_run"]
)


@pytest.fixture
def runs(user):
    """Make some test runs"""
    available_run = BootcampRunFactory.create(
        start_date=now_in_utc() + timedelta(days=1)
    )
    unavailable_run = BootcampRunFactory.create(
        start_date=now_in_utc() - timedelta(days=1)
    )
    submitted_application_run = BootcampRunFactory.create()
    BootcampApplicationFactory.create(user=user, bootcamp_run=submitted_application_run)
    # Applications by other users should not affect whether the run is available
    BootcampApplicationFactory.create(bootcamp_run=available_run)

    yield RunInfo(
        available_run=available_run,
        unavailable_run=unavailable_run,
        submitted_application_run=submitted_application_run,
    )


# pylint: disable=redefined-outer-name
def test_bootcamp_runs(client, user, runs):
    """The REST API should output a list of serialized bootcamp runs"""
    client.force_login(user)

    full_list_resp = client.get(reverse("bootcamp-runs-list"))
    assert full_list_resp.status_code == HTTP_200_OK
    assert (
        full_list_resp.json()
        == BootcampRunSerializer(
            instance=[
                runs.available_run,
                runs.unavailable_run,
                runs.submitted_application_run,
            ],
            many=True,
        ).data
    )

    available_resp = client.get(f"{reverse('bootcamp-runs-list')}?available=true")
    assert available_resp.status_code == HTTP_200_OK
    assert (
        available_resp.json()
        == BootcampRunSerializer(instance=[runs.available_run], many=True).data
    )


def test_bootcamp_runs_not_logged_in(client):
    """Anonymous users should not be able to access the API"""
    assert client.get(reverse("bootcamp-runs-list")).status_code == HTTP_403_FORBIDDEN
