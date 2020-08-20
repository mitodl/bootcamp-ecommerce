"""
Tests for ecommerce models
"""
import pytest

from main.utils import serialize_model_object
from ecommerce.factories import LineFactory, OrderFactory, ReceiptFactory
from ecommerce.models import Order, Line


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def cybersource_settings(settings):
    """Set Cybersource settings"""
    settings.CYBERSOURCE_SECURITY_KEY = "fake"


def test_order_str():
    """Test Order.__str__"""
    order = LineFactory.create().order
    assert str(order) == "Order {}, status={} for user={}".format(
        order.id, order.status, order.user
    )


def test_line_str():
    """Test Line.__str__"""
    line = LineFactory.create()
    assert str(line) == (
        "Line for {order}, price={price}, bootcamp_run_id={bootcamp_run_id}, description={description}".format(
            order=line.order,
            bootcamp_run_id=line.bootcamp_run_id,
            price=line.price,
            description=line.description,
        )
    )


def test_receipt_str_with_order():
    """Test Receipt.__str__ with an order"""
    receipt = ReceiptFactory.create()
    assert str(receipt) == "Receipt for order {}".format(
        receipt.order.id if receipt.order else None
    )


def test_receipt_str_no_order():
    """Test Receipt.__str__ with no order"""
    receipt = ReceiptFactory.create(order=None)
    assert str(receipt) == "Receipt with no attached order"


def test_to_dict():
    """
    Test Order.to_dict()
    """
    order = OrderFactory.create()
    lines = [LineFactory.create(order=order) for _ in range(5)]
    data = order.to_dict()
    lines_data = data.pop("lines")
    assert serialize_model_object(order) == data
    assert lines_data == [serialize_model_object(line) for line in lines]


def test_empty():
    """If there is no Line there should be an empty string"""
    order = OrderFactory.create()
    assert order.line_description == ""


def test_description():
    """line_description should be line.description of the first line"""
    line = LineFactory.create()
    # Second line should be ignored
    LineFactory.create(order=line.order)
    assert line.order.line_description == line.description


def test_empty_line():
    """If there is no Line there should be an empty string"""
    order = OrderFactory.create()
    assert order.run_title == ""


def test_run_title():
    """run_title should return the bootcamp run title"""
    line = LineFactory.create()
    assert line.order.run_title == line.bootcamp_run.display_title


@pytest.fixture
def lines_fulfilled():
    """Create fulfilled orders and lines"""
    order_fulfilled_1 = OrderFactory.create(status=Order.FULFILLED)
    line_fulfilled_1 = LineFactory.create(order=order_fulfilled_1)
    user = order_fulfilled_1.user
    order_fulfilled_2 = OrderFactory.create(user=user, status=Order.FULFILLED)
    line_fulfilled_2 = LineFactory.create(order=order_fulfilled_2)
    order_created = OrderFactory.create(user=user, status=Order.CREATED)
    LineFactory.create(order=order_created, bootcamp_run=line_fulfilled_1.bootcamp_run)

    yield line_fulfilled_1, line_fulfilled_2, user


# pylint: disable=redefined-outer-name
def test_fulfilled_for_user(lines_fulfilled):
    """
    Test for the fulfilled_for_user classmethod
    """
    line_fulfilled_1, line_fulfilled_2, user = lines_fulfilled
    assert list(Line.fulfilled_for_user(user)) == sorted(
        [line_fulfilled_1, line_fulfilled_2], key=lambda x: x.bootcamp_run_id
    )


def test_for_user_bootcamp_run(lines_fulfilled):
    """
    Test for the for_user_bootcamp_run classmethod
    """
    line_fulfilled_1, _, user = lines_fulfilled
    assert list(Line.for_user_bootcamp_run(user, line_fulfilled_1.bootcamp_run)) == [
        line_fulfilled_1
    ]


def test_total_paid_for_bootcamp_run(lines_fulfilled):
    """
    Test for the total_paid_for_bootcamp_run classmethod
    """
    line_fulfilled_1, _, user = lines_fulfilled
    assert (
        Line.total_paid_for_bootcamp_run(user, line_fulfilled_1.bootcamp_run).get(
            "total"
        )
        == line_fulfilled_1.price
    )


@pytest.mark.parametrize(
    "payment_method, card_type, card_number, expected",
    [
        ["card", "001", "xxxxxxxxxxxx1111", "Visa | xxxxxxxxxxxx1111"],
        ["paypal", "", "", "PayPal"],
    ],
)
def test_payment_method(payment_method, card_type, card_number, expected):
    """
    The payment_method property should calculate a description of the payment method from receipt data
    """
    receipt = ReceiptFactory.create()
    receipt_data = {
        **receipt.data,
        "req_payment_method": payment_method,
        "req_card_type": card_type,
        "req_card_number": card_number,
    }
    receipt.data = receipt_data
    receipt.save()
    receipt.refresh_from_db()

    assert receipt.payment_method == expected
