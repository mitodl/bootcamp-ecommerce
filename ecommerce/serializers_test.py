"""Tests for serializers"""

import pytest

from ecommerce.factories import (
    BootcampApplicationFactory,
    LineFactory,
    OrderFactory,
    ReceiptFactory,
)
from ecommerce.models import Order
from ecommerce.serializers import (
    ApplicationOrderSerializer,
    CheckoutDataSerializer,
    LineSerializer,
    OrderPartialSerializer,
    OrderSerializer,
    PaymentSerializer,
)
from klasses.factories import InstallmentFactory
from klasses.serializers import BootcampRunSerializer, InstallmentSerializer
from main.utils import serializer_date_format

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "payload, is_valid",
    [
        [{"payment_amount": "345", "application_id": 3}, True],
        [{"payment_amount": "-3", "application_id": 3}, False],
        [{"payment_amount": "345"}, False],
        [{"application_id": "345"}, False],
    ],
)
def test_validation(payload, is_valid):
    """
    Assert that validation is turned on for the things we care about
    """
    assert is_valid == PaymentSerializer(data=payload).is_valid()


@pytest.fixture
def line():
    """Create a Line and Order"""
    yield LineFactory.create()


def test_orderpartial_serializer(line):
    """
    Test order partial serializer result
    """
    expected = {
        "id": line.order.id,
        "status": line.order.status,
        "created_on": serializer_date_format(line.order.created_on),
        "updated_on": serializer_date_format(line.order.updated_on),
    }
    assert OrderPartialSerializer(line.order).data == expected


@pytest.mark.parametrize(
    "has_receipt, payment_type, expected_payment_method",
    [
        [True, Order.CYBERSOURCE_TYPE, "PayPal"],
        [False, Order.CYBERSOURCE_TYPE, None],
        [True, Order.WIRE_TRANSFER_TYPE, "Wire Transfer"],
        [False, Order.WIRE_TRANSFER_TYPE, "Wire Transfer"],
    ],
)
def test_application_order_serializer(
    line, has_receipt, payment_type, expected_payment_method, settings
):
    """
    Test application order serializer result
    """
    settings.CYBERSOURCE_SECURITY_KEY = "secure!"
    order = line.order
    order.payment_type = payment_type
    order.save()
    if has_receipt:
        ReceiptFactory.create(order=order, data={"req_payment_method": "paypal"})

    assert ApplicationOrderSerializer(order).data == {
        "id": order.id,
        "status": order.status,
        "total_price_paid": line.price,
        "created_on": serializer_date_format(order.created_on),
        "updated_on": serializer_date_format(order.updated_on),
        "payment_method": expected_payment_method,
    }


def test_line_serializer(line):
    """
    Test for line serializer result
    """
    expected = {
        "run_key": line.bootcamp_run.run_key,
        "description": line.description,
        "price": line.price,
        "order": {
            "id": line.order.id,
            "status": line.order.status,
            "created_on": serializer_date_format(line.order.created_on),
            "updated_on": serializer_date_format(line.order.updated_on),
        },
    }

    assert LineSerializer(line).data == expected


@pytest.mark.parametrize("has_paid", [True, False])
def test_checkout_data(has_paid):
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
            bootcamp_run=run,
        )

    InstallmentFactory.create(bootcamp_run=run)

    assert CheckoutDataSerializer(instance=application).data == {
        "id": application.id,
        "bootcamp_run": BootcampRunSerializer(application.bootcamp_run).data,
        "installments": [
            InstallmentSerializer(installment).data
            for installment in run.installment_set.all()
        ],
        "payments": [LineSerializer(line).data] if has_paid else [],
        "total_paid": application.total_paid,
        "total_price": application.price,
    }


def test_order_serializer():
    """OrderSerializer should return expected data"""
    order = OrderFactory.create()
    assert OrderSerializer(instance=order).data == {
        "id": order.id,
        "status": order.status,
        "application_id": order.application.id,
        "created_on": serializer_date_format(order.created_on),
        "updated_on": serializer_date_format(order.updated_on),
    }
