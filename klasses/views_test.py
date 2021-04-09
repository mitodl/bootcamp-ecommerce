"""Views for bootcamps"""
from collections import namedtuple
from datetime import timedelta

from django.urls import reverse
import pytest
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from applications.constants import AppStates
from applications.factories import BootcampApplicationFactory
from klasses.factories import BootcampRunFactory
from klasses.serializers import BootcampRunSerializer
from main.utils import now_in_utc


pytestmark = pytest.mark.django_db


RunInfo = namedtuple(
    "RunInfo",
    ["available_run", "alumni_run", "unavailable_run", "submitted_application_run"],
)


@pytest.fixture
def runs(user):
    """Make some test runs"""
    available_run = BootcampRunFactory.create(
        start_date=now_in_utc() + timedelta(days=1)
    )
    alumni_run = BootcampRunFactory.create(
        allows_skipped_steps=True, start_date=now_in_utc() + timedelta(days=1)
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
        alumni_run=alumni_run,
        unavailable_run=unavailable_run,
        submitted_application_run=submitted_application_run,
    )


# pylint: disable=redefined-outer-name
@pytest.mark.parametrize(
    "is_alumni, user_has_bought_one_bootcamp",
    [(False, False), (True, False), (False, True)],
)
def test_bootcamp_runs(client, user, runs, is_alumni, user_has_bought_one_bootcamp):
    """The REST API should output a list of serialized bootcamp runs"""
    client.force_login(user)

    all_runs = [
        runs.available_run,
        runs.unavailable_run,
        runs.submitted_application_run,
    ]
    available_runs = [runs.available_run]

    if is_alumni:
        user.profile.can_skip_application_steps = True
        user.profile.save()
        all_runs.insert(1, runs.alumni_run)
        available_runs.insert(1, runs.alumni_run)

    if user_has_bought_one_bootcamp:
        application = runs.submitted_application_run.applications.first()
        application.state = AppStates.COMPLETE.value
        application.save()
        all_runs.insert(1, runs.alumni_run)
        available_runs.insert(1, runs.alumni_run)

    full_list_resp = client.get(reverse("bootcamp-runs-list"))
    assert full_list_resp.status_code == HTTP_200_OK
    assert (
        full_list_resp.json()
        == BootcampRunSerializer(instance=all_runs, many=True).data
    )

    available_resp = client.get(f"{reverse('bootcamp-runs-list')}?available=true")
    assert available_resp.status_code == HTTP_200_OK
    assert (
        available_resp.json()
        == BootcampRunSerializer(instance=available_runs, many=True).data
    )


def test_bootcamp_runs_not_logged_in(client):
    """Anonymous users should not be able to access the API"""
    assert client.get(reverse("bootcamp-runs-list")).status_code == HTTP_403_FORBIDDEN
