"""Tests for serializers"""
from decimal import Decimal
import pytest

from main.test_utils import serializer_date_format
from ecommerce.api import get_total_paid
from ecommerce.factories import (
    LineFactory,
    BootcampApplicationFactory,
)
from ecommerce.models import Order
from ecommerce.serializers import (
    PaymentSerializer,
    OrderPartialSerializer,
    LineSerializer,
    ApplicationOrderSerializer,
    CheckoutDataSerializer,
)
from klasses.factories import InstallmentFactory


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("payload, is_valid", [
    [{"payment_amount": "345", "run_key": 3}, True],
    [{"payment_amount": "-3", "run_key": 3}, False],
    [{"payment_amount": "345"}, False],
    [{"run_key": "345"}, False],
])
def test_validation(payload, is_valid):
    """
    Assert that validation is turned on for the things we care about
    """
    assert is_valid == PaymentSerializer(data=payload).is_valid()


@pytest.fixture
def line():
    """Create a Line and Order"""
    yield LineFactory.create()


# pylint: disable=redefined-outer-name
def test_orderpartial_serializer(line):
    """
    Test order partial serializer result
    """
    expected = {
        'id': line.order.id,
        'status': line.order.status,
        'created_on': serializer_date_format(line.order.created_on),
        'updated_on': serializer_date_format(line.order.updated_on),
    }
    assert OrderPartialSerializer(line.order).data == expected


def test_application_order_serializer(line):
    """
    Test application order serializer result
    """
    assert ApplicationOrderSerializer(line.order).data == {
        'id': line.order.id,
        'status': line.order.status,
        'total_price_paid': line.price,
        'created_on': serializer_date_format(line.order.created_on),
        'updated_on': serializer_date_format(line.order.updated_on),
    }


def test_line_serializer(line):
    """
    Test for line serializer result
    """
    expected = {
        'run_key': line.run_key,
        'description': line.description,
        'price': line.price,
        'order': {
            'id': line.order.id,
            'status': line.order.status,
            'created_on': serializer_date_format(line.order.created_on),
            'updated_on': serializer_date_format(line.order.updated_on),
        }
    }

    assert LineSerializer(line).data == expected


@pytest.mark.parametrize("has_paid", [True, False])
def test_checkout_data(mocker, has_paid):
    """
    Test checkout data serializer
    """
    application = BootcampApplicationFactory.create()
    user = application.user
    run = application.bootcamp_run

    if has_paid:
        line = LineFactory.create(
            order__status=Order.FULFILLED,
            order__application=application,
            order__user=user,
            run_key=run.run_key,
        )

    InstallmentFactory.create(bootcamp_run=run)

    request_mock = mocker.Mock(user=user)
    assert CheckoutDataSerializer(instance=application, context={"request": request_mock}).data == {
        "id": application.id,
        "bootcamp_run": {
            "id": run.id,
            "bootcamp": {
                "id": run.bootcamp.id,
                "title": run.bootcamp.title,
            },
            "title": run.title,
            "run_key": run.run_key,
            "start_date": serializer_date_format(run.start_date),
            "end_date": serializer_date_format(run.end_date),
        },
        "installments": [
            {
                "amount": installment.amount,
                "deadline": serializer_date_format(installment.deadline),
            } for installment in run.installment_set.all()
        ],
        "payments": [
            {
                "order": {
                    "id": line.order.id,
                    "status": Order.FULFILLED,
                    "created_on": serializer_date_format(line.order.created_on),
                    "updated_on": serializer_date_format(line.order.updated_on),
                },
                "run_key": line.run_key,
                "price": line.price,
                "description": line.description,
            }
        ] if has_paid else [],
        "total_paid": get_total_paid(user=user, run_key=run.run_key, application_id=application.id),
        "total_price": run.personal_price(user) or Decimal(0),
    }
