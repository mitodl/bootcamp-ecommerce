"""Tests for klass related models"""
from datetime import datetime

import pytest
from pytz import utc

from klasses.factories import InstallmentFactory, KlassFactory
from klasses.models import BootcampAdmissionCache
from profiles.factories import UserFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access

pytestmark = pytest.mark.django_db


def test_klass_price():
    """Price should be sum total of all installments for that klass"""
    installment_1 = InstallmentFactory.create()
    klass = installment_1.klass
    installment_2 = InstallmentFactory.create(klass=klass)
    # Create an unrelated installment to show that it doesn't affect the price
    InstallmentFactory.create()

    assert klass.price == installment_1.amount + installment_2.amount


def test_klass_payment_deadline():
    """Price should be sum total of all installments for that klass"""
    installment_1 = InstallmentFactory.create(deadline=None)
    klass = installment_1.klass
    InstallmentFactory.create(
        klass=klass,
        deadline=datetime(year=2017, month=1, day=1, tzinfo=utc)
    )
    installment_2 = InstallmentFactory.create(
        klass=klass,
        deadline=datetime(year=2017, month=2, day=1, tzinfo=utc)
    )

    assert klass.payment_deadline == installment_2.deadline


def test_klass_formatted_date_range():
    """Test that the formatted_date_range property returns expected values with various start/end dates"""
    base_date = datetime(year=2017, month=1, day=1)
    date_same_month = datetime(year=2017, month=1, day=10)
    date_different_month = datetime(year=2017, month=2, day=1)
    date_different_year = datetime(year=2018, month=1, day=1)
    klass = KlassFactory.build(start_date=base_date, end_date=date_same_month)
    assert klass.formatted_date_range == 'Jan 1 - 10 2017'
    klass = KlassFactory.build(start_date=base_date, end_date=date_different_month)
    assert klass.formatted_date_range == 'Jan 1 - Feb 1 2017'
    klass = KlassFactory.build(start_date=base_date, end_date=date_different_year)
    assert klass.formatted_date_range == 'Jan 1 2017 - Jan 1 2018'
    klass = KlassFactory.build(start_date=base_date, end_date=None)
    assert klass.formatted_date_range == 'Jan 1 2017'
    klass = KlassFactory.build(start_date=None, end_date=None)
    assert klass.formatted_date_range == ''


def test_klass_display_title():
    """Test that the display_title property matches expectations"""
    bootcamp_title = 'Bootcamp 1'
    klass_with_date = KlassFactory.build(bootcamp__title=bootcamp_title, start_date=datetime.now())
    assert klass_with_date.display_title == '{}, {}'.format(bootcamp_title, klass_with_date.formatted_date_range)
    klass_without_dates = KlassFactory.build(bootcamp__title=bootcamp_title, start_date=None, end_date=None)
    assert klass_without_dates.display_title == bootcamp_title


@pytest.fixture()
def test_data():
    """
    Sets up the data for all the tests in this module
    """
    user1 = UserFactory.create(email='foo@example.com')
    user2 = UserFactory.create(email='bar@example.com')
    num_klasses = 3
    for klass_key in range(100, 100+num_klasses):
        klass = KlassFactory.create(klass_key=klass_key)
        for user in (user1, user2, ):
            BootcampAdmissionCache.objects.create(user=user, klass=klass, data={'foo': 'bar'})
    return user1, num_klasses


def test_bootcamp_adm_cache_user_qset(test_data):
    """
    Tests the user_qset filter
    """
    user, num_klasses = test_data
    assert BootcampAdmissionCache.objects.count() == num_klasses*2
    assert BootcampAdmissionCache.user_qset(user).count() == num_klasses
    for adm_cache in BootcampAdmissionCache.user_qset(user):
        assert adm_cache.user == user


def test_bootcamp_adm_cache_delete_all_but(test_data):
    """
    Tests the delete_all_but classmethod
    """
    user, num_klasses = test_data
    assert BootcampAdmissionCache.objects.count() == num_klasses*2
    assert BootcampAdmissionCache.user_qset(user).count() == num_klasses
    BootcampAdmissionCache.delete_all_but(user, [100])
    assert BootcampAdmissionCache.user_qset(user).count() == 1
    assert BootcampAdmissionCache.user_qset(user).first().klass.klass_key == 100
