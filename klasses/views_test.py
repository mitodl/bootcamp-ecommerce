"""Views for bootcamps"""
from datetime import timedelta

from django.urls import reverse
import pytest
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_403_FORBIDDEN,
)

from klasses.factories import BootcampRunFactory
from klasses.models import BootcampRunEnrollment
from klasses.serializers import BootcampRunSerializer
from main.utils import now_in_utc


pytestmark = pytest.mark.django_db


@pytest.fixture
def runs(user):
    """Make some test runs"""
    run = BootcampRunFactory.create()
    unavailable_run = BootcampRunFactory.create(start_date=now_in_utc()+timedelta(days=1))
    already_enrolled_run = BootcampRunFactory.create()
    BootcampRunEnrollment.objects.create(user=user, bootcamp_run=already_enrolled_run)

    return run, unavailable_run, already_enrolled_run


# pylint: disable=redefined-outer-name
def test_bootcamp_runs(client, user, runs):
    """The REST API should output a list of serialized bootcamp runs"""
    run, unavailable_run, already_enrolled_run = runs
    client.force_login(user)

    full_list_resp = client.get(reverse("bootcamp-runs-list"))
    assert full_list_resp.status_code == HTTP_200_OK
    assert full_list_resp.json() == BootcampRunSerializer(
        instance=[
            run, unavailable_run, already_enrolled_run
        ], many=True
    ).data

    available_resp = client.get(f"{reverse('bootcamp-runs-list')}?available=true")
    assert available_resp.status_code == HTTP_200_OK
    assert available_resp.json() == BootcampRunSerializer(instance=[run], many=True).data


def test_bootcamp_runs_not_logged_in(client):
    """Anonymous users should not be able to access the API"""
    assert client.get(reverse("bootcamp-runs-list")).status_code == HTTP_403_FORBIDDEN
