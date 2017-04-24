"""
Tests for api module
"""
from decimal import Decimal
from unittest.mock import PropertyMock

import pytest

from ecommerce.factories import OrderFactory, LineFactory
from ecommerce.models import Order, Line
from ecommerce.serializers import LineSerializer
from klasses.api import (
    serialize_user_klass,
    serialize_user_klasses,
)
from klasses.bootcamp_admissions_client import BootcampAdmissionClient
from klasses.factories import KlassFactory, InstallmentFactory
from klasses.serializers import InstallmentSerializer
from profiles.factories import UserFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


@pytest.fixture()
def setup_test_data():
    """
    Sets up the data for all the tests in this module
    """
    user = UserFactory.create()
    klass_paid = KlassFactory.create()
    klass_not_paid = KlassFactory.create()

    InstallmentFactory.create(klass=klass_paid)
    InstallmentFactory.create(klass=klass_not_paid)

    order = OrderFactory.create(user=user, status=Order.FULFILLED)
    LineFactory.create(order=order, klass_id=klass_paid.klass_id, price=627.34)

    return user, klass_paid, klass_not_paid


def test_serialize_user_klass_bootclient_equivalent(setup_test_data):
    """
    Test for serialize_user_klass to verify that passing or not passing the bootcamp client is equivalent.
    """
    user, klass_paid, _ = setup_test_data

    assert serialize_user_klass(user, klass_paid) == serialize_user_klass(
        user, klass_paid, BootcampAdmissionClient(user.email))


def test_serialize_user_klass_paid(setup_test_data):
    """
    Test for serialize_user_klass for a paid klass
    """
    user, klass_paid, _ = setup_test_data

    expected_ret = {
        "klass_id": klass_paid.klass_id,
        "klass_name": klass_paid.title,
        "start_date": klass_paid.start_date,
        "end_date": klass_paid.end_date,
        "price": klass_paid.price,
        "is_user_eligible_to_pay": True,
        "total_paid": Decimal('627.34'),
        "payments": LineSerializer(Line.for_user_klass(user, klass_paid.klass_id), many=True).data,
        "installments": InstallmentSerializer(
            klass_paid.installment_set.order_by('installment_number'), many=True).data,
    }
    assert expected_ret == serialize_user_klass(user, klass_paid)


def test_serialize_user_klass_not_paid(setup_test_data):
    """
    Test for serialize_user_klass for a not paid klass
    """
    user, _, klass_not_paid = setup_test_data

    expected_ret = {
        "klass_id": klass_not_paid.klass_id,
        "klass_name": klass_not_paid.title,
        "start_date": klass_not_paid.start_date,
        "end_date": klass_not_paid.end_date,
        "price": klass_not_paid.price,
        "is_user_eligible_to_pay": True,
        "total_paid": Decimal('0.00'),
        "payments": [],
        "installments": InstallmentSerializer(
            klass_not_paid.installment_set.order_by('installment_number'), many=True).data,
    }
    assert expected_ret == serialize_user_klass(user, klass_not_paid)


def test_serialize_user_klasses(setup_test_data):
    """
    Test for serialize_user_klasses in normal case
    """
    user, klass_paid, klass_not_paid = setup_test_data
    expected_ret = [
        {
            "klass_id": klass_paid.klass_id,
            "klass_name": klass_paid.title,
            "start_date": klass_paid.start_date,
            "end_date": klass_paid.end_date,
            "price": klass_paid.price,
            "is_user_eligible_to_pay": True,
            "total_paid": Decimal('627.34'),
            "payments": LineSerializer(Line.for_user_klass(user, klass_paid.klass_id), many=True).data,
            "installments": InstallmentSerializer(
                klass_paid.installment_set.order_by('installment_number'), many=True).data,
        },
        {
            "klass_id": klass_not_paid.klass_id,
            "klass_name": klass_not_paid.title,
            "start_date": klass_not_paid.start_date,
            "end_date": klass_not_paid.end_date,
            "price": klass_not_paid.price,
            "is_user_eligible_to_pay": True,
            "total_paid": Decimal('0.00'),
            "payments": [],
            "installments": InstallmentSerializer(
                klass_not_paid.installment_set.order_by('installment_number'), many=True).data,
        }
    ]
    assert sorted(expected_ret, key=lambda x: x['klass_id']) == serialize_user_klasses(user)


def test_serialize_user_klasses_paid_not_payable(setup_test_data, mocker):
    """
    Test for serialize_user_klasses in case the user is not eligible to pay but she has already paid for the klass
    """
    user, klass_paid, klass_not_paid = setup_test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_klasses_ids',
        new_callable=PropertyMock,
        return_value=[klass_not_paid.klass_id],
    )
    res = serialize_user_klasses(user)
    assert klass_paid.klass_id in [klass['klass_id'] for klass in res]
    for klass in res:
        if klass['klass_id'] == klass_paid.klass_id:
            break
    assert klass['is_user_eligible_to_pay'] is False  # pylint: disable=undefined-loop-variable
