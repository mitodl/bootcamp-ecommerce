"""Tests for klass related models"""
from datetime import datetime, timedelta

import pytest
from pytz import UTC

from klasses.factories import InstallmentFactory, KlassFactory, PersonalPriceFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access
from profiles.factories import ProfileFactory

pytestmark = pytest.mark.django_db


# Klass model tests

@pytest.fixture()
def test_data(db):
    installment = InstallmentFactory.create()
    klass = installment.klass
    return installment, klass


def test_klass_price(test_data):
    """Price should be sum total of all installments for that klass"""
    installment_1, klass = test_data
    installment_2 = InstallmentFactory.create(klass=klass)
    # Create an unrelated installment to show that it doesn't affect the price
    InstallmentFactory.create()

    assert klass.price == installment_1.amount + installment_2.amount


def test_klass_personal_price(test_data):
    """Price should be person's custom cost if any or default price"""
    _, klass = test_data
    profile = ProfileFactory.create(fluidreview_id=100)
    assert klass.personal_price(profile.user) == klass.price
    personal_price = PersonalPriceFactory.create(klass=klass, user=profile.user)
    assert klass.personal_price(profile.user) == personal_price.price
    assert profile.user.klass_prices.filter(klass=klass).first().price == personal_price.price


def test_klass_payment_deadline():
    """Price should be sum total of all installments for that klass"""
    installment_1 = InstallmentFactory.create(deadline=datetime(year=2017, month=1, day=1, tzinfo=UTC))
    klass = installment_1.klass
    installment_2 = InstallmentFactory.create(
        klass=klass,
        deadline=datetime(year=2017, month=2, day=1, tzinfo=UTC)
    )

    assert klass.payment_deadline == installment_2.deadline


def test_klass_formatted_date_range():
    """Test that the formatted_date_range property returns expected values with various start/end dates"""
    base_date = datetime(year=2017, month=1, day=1)
    date_same_month = datetime(year=2017, month=1, day=10)
    date_different_month = datetime(year=2017, month=2, day=1)
    date_different_year = datetime(year=2018, month=1, day=1)
    klass = KlassFactory.build(start_date=base_date, end_date=date_same_month)
    assert klass.formatted_date_range == 'Jan 1 - 10, 2017'
    klass = KlassFactory.build(start_date=base_date, end_date=date_different_month)
    assert klass.formatted_date_range == 'Jan 1 - Feb 1, 2017'
    klass = KlassFactory.build(start_date=base_date, end_date=date_different_year)
    assert klass.formatted_date_range == 'Jan 1, 2017 - Jan 1, 2018'
    klass = KlassFactory.build(start_date=base_date, end_date=None)
    assert klass.formatted_date_range == 'Jan 1, 2017'
    klass = KlassFactory.build(start_date=None, end_date=None)
    assert klass.formatted_date_range == ''


def test_klass_display_title():
    """Test that the display_title property matches expectations"""
    bootcamp_title = 'Bootcamp 1'
    klass_with_date = KlassFactory.build(bootcamp__title=bootcamp_title, start_date=datetime.now())
    assert klass_with_date.display_title == '{}, {}'.format(bootcamp_title, klass_with_date.formatted_date_range)
    klass_without_dates = KlassFactory.build(bootcamp__title=bootcamp_title, start_date=None, end_date=None)
    assert klass_without_dates.display_title == bootcamp_title


def test_next_installment():
    """
    It should return the installment with the closest date to now in the future
    """
    installment_past = InstallmentFactory.create(deadline=datetime.now(tz=UTC)-timedelta(weeks=1))
    klass = installment_past.klass
    assert klass.next_installment is None
    installment = InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(weeks=1))
    InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(weeks=2))
    assert klass.next_installment == installment


def test_next_payment_deadline_days():
    """
    Number of days until the next deadline
    """
    installment_past = InstallmentFactory.create(deadline=datetime.now(tz=UTC)-timedelta(weeks=1))
    klass = installment_past.klass
    assert klass.next_payment_deadline_days is None
    InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(days=3, hours=1))
    assert klass.next_payment_deadline_days == 3


def test_total_due_by_next_deadline():
    """
    The total amount of money that should be paid until the next deadline
    """
    installment_past = InstallmentFactory.create(deadline=datetime.now(tz=UTC)-timedelta(weeks=1))
    klass = installment_past.klass
    assert klass.total_due_by_next_deadline == klass.price
    installment_next = InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(days=3))
    InstallmentFactory.create(klass=klass, deadline=datetime.now(tz=UTC)+timedelta(weeks=3))
    assert klass.total_due_by_next_deadline == installment_past.amount + installment_next.amount
