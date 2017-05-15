"""
Tests for tasks module
"""

import pytest

from klasses import tasks
from klasses.factories import KlassFactory
from klasses.models import BootcampAdmissionCache
from profiles.factories import UserFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access

pytestmark = pytest.mark.django_db


expected_payable_klasses = [
    {
        "klass_id": 16,
        "klass_name": "Class 1",
        "status": "scholarship_not_awarded",
        "is_user_eligible_to_pay": True
    },
    {
        "klass_id": 23,
        "klass_name": "Class 2 Student",
        "status": "admitted",
        "is_user_eligible_to_pay": True
    },
    {
        "klass_id": 44,
        "klass_name": "Class 44 Student",
        "status": "admitted",
        "is_user_eligible_to_pay": True
    }
]
expected_payable_klass_keys = [klass['klass_id'] for klass in expected_payable_klasses]
expected_payable_klass_lookup = {klass['klass_id']: klass for klass in expected_payable_klasses}


@pytest.fixture()
def test_data():
    """
    Sets up the data for all the tests in this module
    """
    user = UserFactory.create(email='foo@example.com')
    cacheable_klasses_keys = expected_payable_klass_keys[:-1]
    for klass_key in cacheable_klasses_keys:
        KlassFactory.create(klass_key=klass_key)
    return user, cacheable_klasses_keys


def test_task_passthrough(test_data, mocker):
    """
    Test that async_cache_admissions calls _cache_admissions with some params
    """
    mocked_func = mocker.patch('klasses.tasks._cache_admissions', autospec=True)
    user, _ = test_data
    tasks.async_cache_admissions(user.email, expected_payable_klasses)
    mocked_func.assert_called_once_with(user.email, expected_payable_klasses)


def test_cache_admissions_happy_path(test_data):
    """
    Test _cache_admissions when everything is fine
    """
    user, cacheable_klasses_keys = test_data
    assert BootcampAdmissionCache.objects.count() == 0
    tasks._cache_admissions(user.email, expected_payable_klasses)
    assert list(
        BootcampAdmissionCache.objects.filter(user=user).values_list('klass__klass_key', flat=True)
    ) == cacheable_klasses_keys
    for cached_elem in BootcampAdmissionCache.objects.filter(user=user):
        assert cached_elem.data == expected_payable_klass_lookup[cached_elem.klass.klass_key]
    assert BootcampAdmissionCache.objects.filter(user=user).filter(
        klass__klass_key=expected_payable_klass_keys[-1]).exists() is False


def test_cache_admissions_no_user():
    """
    Test _cache_admissions when there is no such user with the provided email
    """
    assert BootcampAdmissionCache.objects.count() == 0
    tasks._cache_admissions('bar@example.com', expected_payable_klasses)
    assert BootcampAdmissionCache.objects.count() == 0


def test_cache_admissions_delete_everything_else(test_data):
    """
    Test _cache_admission in case there are elements in the cache that need to be removed
    """
    user, _ = test_data
    klass = KlassFactory.create(klass_key=99)
    BootcampAdmissionCache.objects.create(user=user, klass=klass, data={'foo': 'bar'})
    assert BootcampAdmissionCache.objects.count() == 1
    tasks._cache_admissions(user.email, {})
    assert BootcampAdmissionCache.objects.count() == 0
