"""
conftest for pytest in this module
"""
from datetime import timedelta

from types import SimpleNamespace
from unittest.mock import Mock

import factory
import pytest

from ecommerce.factories import OrderFactory
from klasses.factories import (
    BootcampFactory,
    BootcampRunFactory,
    BootcampRunEnrollmentFactory,
)
from main.utils import now_in_utc


@pytest.fixture()
def mocked_requests_get(mocker):
    """
    Generic mock for requests.get
    """
    mocked_get_func = mocker.patch("requests.get", autospec=True)
    mocked_response = Mock()
    mocked_get_func.return_value = mocked_response
    return SimpleNamespace(request=mocked_get_func, response=mocked_response)


@pytest.fixture()
def patched_create_run_enrollments(mocker):
    """patched create_run_enrollments"""
    return mocker.patch("klasses.api.create_run_enrollments", return_value=([], False))


@pytest.fixture()
def patched_deactivate_run_enrollment(mocker):
    """patched deactivate_run_enrollment"""
    return mocker.patch("klasses.api.deactivate_run_enrollment", return_value=[])


@pytest.fixture()
def enrollment_data(user):
    """enrollment data for testing"""
    bootcamps = BootcampFactory.create_batch(2)
    enrollments = BootcampRunEnrollmentFactory.create_batch(
        3,
        user=user,
        active=factory.Iterator([False, True, True]),
        bootcamp_run__bootcamp=factory.Iterator(
            [bootcamps[0], bootcamps[0], bootcamps[1]]
        ),
    )
    unenrollable_run = BootcampRunFactory.create(
        end_date=now_in_utc() - timedelta(days=1)
    )
    order = OrderFactory.create(user=user)
    return SimpleNamespace(
        bootcamps=bootcamps,
        enrollments=enrollments,
        unenrollable_run=unenrollable_run,
        order=order,
    )
