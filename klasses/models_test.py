"""Tests for bootcamp related models"""
from datetime import datetime, timedelta

import pytest
from pytz import UTC
from mitol.common.utils import now_in_utc

from ecommerce.test_utils import create_test_application
from klasses.constants import ENROLL_CHANGE_STATUS_DEFERRED
from klasses.factories import (
    InstallmentFactory,
    BootcampRunFactory,
    BootcampRunEnrollmentFactory,
    PersonalPriceFactory,
    BootcampRunCertificateFactory,
)
from main.test_utils import format_as_iso8601
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
    """is_payable should return True if the payment deadline is set and is in the future"""
    bootcamp_run = None
    if future_start_date is None:
        start_date = None
        bootcamp_run = BootcampRunFactory.build(start_date=start_date)
    elif future_start_date:
        start_date = now_in_utc() + timedelta(days=10)
    else:
        start_date = now_in_utc() - timedelta(days=10)
    if not bootcamp_run:
        installment = InstallmentFactory.create(deadline=start_date)
        bootcamp_run = installment.bootcamp_run
    assert bootcamp_run.is_payable is expected_result


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


@pytest.mark.parametrize("end_days, expected", [[None, True], [1, True], [-1, False]])
def test_course_run_not_beyond_enrollment(end_days, expected):
    """
    Test that CourseRun.is_beyond_enrollment returns the expected boolean value
    """
    now = now_in_utc()
    end_date = None if end_days is None else now + timedelta(days=end_days)

    assert (
        BootcampRunFactory.create(end_date=end_date).is_not_beyond_enrollment
        is expected
    )


def test_audit(user):
    """Test audit table serialization"""

    enrollment = BootcampRunEnrollmentFactory.create()
    enrollment.save_and_log(user)

    expected = {
        "active": enrollment.active,
        "change_status": enrollment.change_status,
        "created_on": format_as_iso8601(enrollment.created_on),
        "email": enrollment.user.email,
        "full_name": enrollment.user.profile.name,
        "id": enrollment.id,
        "updated_on": format_as_iso8601(enrollment.updated_on),
        "user": enrollment.user.id,
        "username": enrollment.user.username,
        "bootcamp_run": enrollment.bootcamp_run.id,
        "novoed_sync_date": enrollment.novoed_sync_date,
        "user_certificate_is_blocked": enrollment.user_certificate_is_blocked,
    }

    assert (
        enrollment.get_audit_class().objects.get(enrollment=enrollment).data_after
        == expected
    )


def test_get_related_field_name():
    """Test audit table related_field_name"""
    assert (
        BootcampRunEnrollmentFactory._meta.model.get_audit_class().get_related_field_name()
        == "enrollment"
    )


def test_bootcamp_run_enrollment_to_dict():
    """Test to_dict method for bootcamp run enrollment"""
    enrollment = BootcampRunEnrollmentFactory.create()

    expected = {
        "active": enrollment.active,
        "change_status": enrollment.change_status,
        "created_on": format_as_iso8601(enrollment.created_on),
        "email": enrollment.user.email,
        "full_name": enrollment.user.profile.name,
        "id": enrollment.id,
        "updated_on": format_as_iso8601(enrollment.updated_on),
        "user": enrollment.user.id,
        "username": enrollment.user.username,
        "bootcamp_run": enrollment.bootcamp_run.id,
        "novoed_sync_date": enrollment.novoed_sync_date,
        "user_certificate_is_blocked": enrollment.user_certificate_is_blocked,
    }

    assert enrollment.to_dict() == expected


def test_deactivate_and_save():
    """Test deactivate_and_save method for bootcamp run enrollment"""
    enrollment = BootcampRunEnrollmentFactory.create()

    assert enrollment.active
    assert enrollment.change_status is None

    enrollment.deactivate_and_save(ENROLL_CHANGE_STATUS_DEFERRED)

    assert not enrollment.active
    assert enrollment.change_status == ENROLL_CHANGE_STATUS_DEFERRED


def test_reactivate_and_save():
    """Test reactivate_and_save method for bootcamp run enrollment"""
    enrollment = BootcampRunEnrollmentFactory.create(active=False, change_status=None)

    assert not enrollment.active
    assert enrollment.change_status is None

    enrollment.reactivate_and_save()

    assert enrollment.active
    assert enrollment.change_status is None
