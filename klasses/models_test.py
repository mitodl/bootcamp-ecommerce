"""Tests for bootcamp related models"""
from datetime import datetime, timedelta

import pytest
from pytz import UTC

from klasses.factories import InstallmentFactory, BootcampRunFactory, PersonalPriceFactory
from main.utils import now_in_utc
from profiles.factories import ProfileFactory

pytestmark = pytest.mark.django_db
# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access


@pytest.fixture()
def test_data(db):
    installment = InstallmentFactory.create()
    bootcamp_run = installment.bootcamp_run
    return installment, bootcamp_run


def test_bootcamp_run_price(test_data):
    """Price should be sum total of all installments for that bootcamp run"""
    installment_1, bootcamp_run = test_data
    installment_2 = InstallmentFactory.create(bootcamp_run=bootcamp_run)
    # Create an unrelated installment to show that it doesn't affect the price
    InstallmentFactory.create()

    assert bootcamp_run.price == installment_1.amount + installment_2.amount


def test_bootcamp_run_personal_price(test_data):
    """Price should be person's custom cost if any or default price"""
    _, bootcamp_run = test_data
    profile = ProfileFactory.create(fluidreview_id=100)
    assert bootcamp_run.personal_price(profile.user) == bootcamp_run.price
    personal_price = PersonalPriceFactory.create(bootcamp_run=bootcamp_run, user=profile.user)
    assert bootcamp_run.personal_price(profile.user) == personal_price.price
    assert profile.user.run_prices.filter(bootcamp_run=bootcamp_run).first().price == personal_price.price


def test_bootcamp_run_payment_deadline():
    """Price should be sum total of all installments for that bootcamp run"""
    installment_1 = InstallmentFactory.create(deadline=datetime(year=2017, month=1, day=1, tzinfo=UTC))
    bootcamp_run = installment_1.bootcamp_run
    installment_2 = InstallmentFactory.create(
        bootcamp_run=bootcamp_run,
        deadline=datetime(year=2017, month=2, day=1, tzinfo=UTC)
    )

    assert bootcamp_run.payment_deadline == installment_2.deadline


def test_bootcamp_run_formatted_date_range():
    """Test that the formatted_date_range property returns expected values with various start/end dates"""
    base_date = datetime(year=2017, month=1, day=1)
    date_same_month = datetime(year=2017, month=1, day=10)
    date_different_month = datetime(year=2017, month=2, day=1)
    date_different_year = datetime(year=2018, month=1, day=1)
    bootcamp_run = BootcampRunFactory.build(start_date=base_date, end_date=date_same_month)
    assert bootcamp_run.formatted_date_range == 'Jan 1 - 10, 2017'
    bootcamp_run = BootcampRunFactory.build(start_date=base_date, end_date=date_different_month)
    assert bootcamp_run.formatted_date_range == 'Jan 1 - Feb 1, 2017'
    bootcamp_run = BootcampRunFactory.build(start_date=base_date, end_date=date_different_year)
    assert bootcamp_run.formatted_date_range == 'Jan 1, 2017 - Jan 1, 2018'
    bootcamp_run = BootcampRunFactory.build(start_date=base_date, end_date=None)
    assert bootcamp_run.formatted_date_range == 'Jan 1, 2017'
    bootcamp_run = BootcampRunFactory.build(start_date=None, end_date=None)
    assert bootcamp_run.formatted_date_range == ''


def test_bootcamp_run_display_title():
    """Test that the display_title property matches expectations"""
    bootcamp_title = 'Bootcamp 1'
    bootcamp_run_with_date = BootcampRunFactory.build(bootcamp__title=bootcamp_title, start_date=datetime.now())
    assert bootcamp_run_with_date.display_title == '{}, {}'.format(
        bootcamp_title, bootcamp_run_with_date.formatted_date_range
    )
    bootcamp_run_without_dates = BootcampRunFactory.build(
        bootcamp__title=bootcamp_title, start_date=None, end_date=None
    )
    assert bootcamp_run_without_dates.display_title == bootcamp_title


def test_next_installment():
    """
    It should return the installment with the closest date to now in the future
    """
    installment_past = InstallmentFactory.create(deadline=now_in_utc()-timedelta(weeks=1))
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.next_installment is None
    installment = InstallmentFactory.create(bootcamp_run=bootcamp_run, deadline=now_in_utc()+timedelta(weeks=1))
    InstallmentFactory.create(bootcamp_run=bootcamp_run, deadline=now_in_utc()+timedelta(weeks=2))
    assert bootcamp_run.next_installment == installment


def test_next_payment_deadline_days():
    """
    Number of days until the next deadline
    """
    installment_past = InstallmentFactory.create(deadline=now_in_utc()-timedelta(weeks=1))
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.next_payment_deadline_days is None
    InstallmentFactory.create(bootcamp_run=bootcamp_run, deadline=now_in_utc()+timedelta(days=3, hours=1))
    assert bootcamp_run.next_payment_deadline_days == 3


def test_total_due_by_next_deadline():
    """
    The total amount of money that should be paid until the next deadline
    """
    installment_past = InstallmentFactory.create(deadline=now_in_utc()-timedelta(weeks=1))
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.total_due_by_next_deadline == bootcamp_run.price
    installment_next = InstallmentFactory.create(
        bootcamp_run=bootcamp_run,
        deadline=now_in_utc()+timedelta(days=3)
    )
    InstallmentFactory.create(bootcamp_run=bootcamp_run, deadline=now_in_utc()+timedelta(weeks=3))
    assert bootcamp_run.total_due_by_next_deadline == installment_past.amount + installment_next.amount
