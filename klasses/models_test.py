"""Tests for bootcamp related models"""
from datetime import datetime, timedelta

import pytest
from pytz import UTC

from ecommerce.test_utils import create_test_application
from klasses.factories import (
    InstallmentFactory,
    BootcampRunFactory,
    PersonalPriceFactory,
    BootcampRunCertificateFactory,
)
from main.utils import now_in_utc
from profiles.factories import ProfileFactory

pytestmark = pytest.mark.django_db
# pylint: disable=missing-docstring,redefined-outer-name,unused-argument,protected-access


@pytest.fixture()
def test_data(db):
    installment = InstallmentFactory.create()
    bootcamp_run = installment.bootcamp_run
    return installment, bootcamp_run


@pytest.fixture
def application():
    """An application for testing"""
    yield create_test_application()


@pytest.fixture
def user(application):
    """A user with social auth"""
    yield application.user


@pytest.fixture
def bootcamp_run(application):
    """
    Creates a purchasable bootcamp run. Bootcamp run price is at least $200, in two installments
    """
    yield application.bootcamp_run


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
    profile = ProfileFactory.create()
    assert bootcamp_run.personal_price(profile.user) == bootcamp_run.price
    personal_price = PersonalPriceFactory.create(
        bootcamp_run=bootcamp_run, user=profile.user
    )
    assert bootcamp_run.personal_price(profile.user) == personal_price.price
    assert (
        profile.user.run_prices.filter(bootcamp_run=bootcamp_run).first().price
        == personal_price.price
    )


def test_bootcamp_run_payment_deadline():
    """Price should be sum total of all installments for that bootcamp run"""
    installment_1 = InstallmentFactory.create(
        deadline=datetime(year=2017, month=1, day=1, tzinfo=UTC)
    )
    bootcamp_run = installment_1.bootcamp_run
    installment_2 = InstallmentFactory.create(
        bootcamp_run=bootcamp_run,
        deadline=datetime(year=2017, month=2, day=1, tzinfo=UTC),
    )

    assert bootcamp_run.payment_deadline == installment_2.deadline


@pytest.mark.parametrize(
    "start_date,end_date,exp_result",
    [
        [
            datetime.strptime("01/01/2020", "%m/%d/%Y"),
            datetime.strptime("01/01/2021", "%m/%d/%Y"),
            "Jan 1, 2020 - Jan 1, 2021",
        ],
        [
            datetime.strptime("01/01/2020", "%m/%d/%Y"),
            datetime.strptime("02/01/2020", "%m/%d/%Y"),
            "Jan 1 - Feb 1, 2020",
        ],
        [
            datetime.strptime("01/01/2020", "%m/%d/%Y"),
            datetime.strptime("01/15/2020", "%m/%d/%Y"),
            "Jan 1 - 15, 2020",
        ],
        [datetime.strptime("01/01/2020", "%m/%d/%Y"), None, "Jan 1, 2020"],
    ],
)
def test_bootcamp_run_formatted_date_range(start_date, end_date, exp_result):
    """Test that the formatted_date_range property returns expected values with various start/end dates"""
    bootcamp_run = BootcampRunFactory.build(start_date=start_date, end_date=end_date)
    assert bootcamp_run.formatted_date_range == exp_result


def test_bootcamp_run_display_title():
    """Test that the display_title property matches expectations"""
    bootcamp_title = "Bootcamp 1"
    bootcamp_run_with_date = BootcampRunFactory.build(
        bootcamp__title=bootcamp_title, start_date=datetime.now()
    )
    assert bootcamp_run_with_date.display_title == "{}, {}".format(
        bootcamp_title, bootcamp_run_with_date.formatted_date_range
    )
    bootcamp_run_without_dates = BootcampRunFactory.build(
        bootcamp__title=bootcamp_title, start_date=None, end_date=None
    )
    assert bootcamp_run_without_dates.display_title == bootcamp_title


@pytest.mark.parametrize(
    "future_start_date,expected_result", [[True, True], [False, False], [None, False]]
)
def test_bootcamp_run_is_payable(future_start_date, expected_result):
    """is_payable should return True if the start date is set and is in the future"""
    if future_start_date is None:
        start_date = None
    elif future_start_date:
        start_date = now_in_utc() + timedelta(days=10)
    else:
        start_date = now_in_utc() - timedelta(days=10)
    run = BootcampRunFactory.build(start_date=start_date)
    assert run.is_payable is expected_result


def test_next_installment():
    """
    It should return the installment with the closest date to now in the future
    """
    installment_past = InstallmentFactory.create(
        deadline=now_in_utc() - timedelta(weeks=1)
    )
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.next_installment is None
    installment = InstallmentFactory.create(
        bootcamp_run=bootcamp_run, deadline=now_in_utc() + timedelta(weeks=1)
    )
    InstallmentFactory.create(
        bootcamp_run=bootcamp_run, deadline=now_in_utc() + timedelta(weeks=2)
    )
    assert bootcamp_run.next_installment == installment


def test_next_payment_deadline_days():
    """
    Number of days until the next deadline
    """
    installment_past = InstallmentFactory.create(
        deadline=now_in_utc() - timedelta(weeks=1)
    )
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.next_payment_deadline_days is None
    InstallmentFactory.create(
        bootcamp_run=bootcamp_run, deadline=now_in_utc() + timedelta(days=3, hours=1)
    )
    assert bootcamp_run.next_payment_deadline_days == 3


def test_total_due_by_next_deadline():
    """
    The total amount of money that should be paid until the next deadline
    """
    installment_past = InstallmentFactory.create(
        deadline=now_in_utc() - timedelta(weeks=1)
    )
    bootcamp_run = installment_past.bootcamp_run
    assert bootcamp_run.total_due_by_next_deadline == bootcamp_run.price
    installment_next = InstallmentFactory.create(
        bootcamp_run=bootcamp_run, deadline=now_in_utc() + timedelta(days=3)
    )
    InstallmentFactory.create(
        bootcamp_run=bootcamp_run, deadline=now_in_utc() + timedelta(weeks=3)
    )
    assert (
        bootcamp_run.total_due_by_next_deadline
        == installment_past.amount + installment_next.amount
    )


def test_bootcamp_run_certificate(bootcamp_run, user):
    """
    test bootcamp run certificates
    """

    certificate = BootcampRunCertificateFactory.create(
        user=user, bootcamp_run=bootcamp_run
    )

    assert certificate.is_revoked is False
    assert certificate.start_end_dates == (
        bootcamp_run.start_date,
        bootcamp_run.end_date,
    )
    assert certificate.link == "/certificate/{uuid}/".format(uuid=certificate.uuid)
    assert str(
        certificate
    ) == "BootcampRunCertificate for user={user}, run={bootcamp_run} ({uuid})".format(
        user=user.username, bootcamp_run=bootcamp_run.id, uuid=certificate.uuid
    )
    certificate.revoke()
    assert certificate.is_revoked is True
    certificate.unrevoke()
    assert certificate.is_revoked is False
