"""
Tests for ecommerce models
"""
import pytest

from main.utils import serialize_model_object
from ecommerce.factories import (
    LineFactory,
    OrderFactory,
    ReceiptFactory,
)
from ecommerce.models import Order, Line
from klasses.factories import BootcampRunFactory
from klasses.models import BootcampRun


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def cybersource_settings(settings):
    """Set Cybersource settings"""
    settings.CYBERSOURCE_SECURITY_KEY = 'fake'


def test_order_str():
    """Test Order.__str__"""
    order = LineFactory.create().order
    assert str(order) == "Order {}, status={} for user={}".format(order.id, order.status, order.user)


def test_line_str():
    """Test Line.__str__"""
    line = LineFactory.create()
    assert str(line) == (
        "Line for {order}, price={price}, run_key={run_key}, description={description}".format(
            order=line.order,
            run_key=line.run_key,
            price=line.price,
            description=line.description,
        )
    )


def test_receipt_str_with_order():
    """Test Receipt.__str__ with an order"""
    receipt = ReceiptFactory.create()
    assert str(receipt) == "Receipt for order {}".format(receipt.order.id if receipt.order else None)


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
    lines_data = data.pop('lines')
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


def test_no_bootcamp_run():
    """If there is no BootcampRun there should be an empty string"""
    line = LineFactory.create()
    assert BootcampRun.objects.filter(run_key=line.run_key).exists() is False
    assert line.order.run_title == ""


def test_run_title():
    """run_title should be bootcamp run title for the given run_key"""
    bootcamp_run = BootcampRunFactory.create()
    line = LineFactory.create(run_key=bootcamp_run.run_key)
    assert line.order.run_title == bootcamp_run.title


@pytest.fixture
def lines_fulfilled():
    order_fulfilled_1 = OrderFactory.create(status=Order.FULFILLED)
    line_fulfilled_1 = LineFactory.create(order=order_fulfilled_1)
    user = order_fulfilled_1.user
    run_key = line_fulfilled_1.run_key
    order_fulfilled_2 = OrderFactory.create(user=user, status=Order.FULFILLED)
    line_fulfilled_2 = LineFactory.create(order=order_fulfilled_2)
    order_created = OrderFactory.create(user=user, status=Order.CREATED)
    line_created = LineFactory.create(order=order_created, run_key=run_key)

    yield line_fulfilled_1, line_fulfilled_2, user, run_key


def test_fulfilled_for_user(lines_fulfilled):
    """
    Test for the fulfilled_for_user classmethod
    """
    line_fulfilled_1, line_fulfilled_2, user, _ = lines_fulfilled
    assert list(Line.fulfilled_for_user(user)) == sorted(
        [line_fulfilled_1, line_fulfilled_2],
        key=lambda x: x.run_key
    )


def test_for_user_bootcamp_run(lines_fulfilled):
    """
    Test for the for_user_bootcamp_run classmethod
    """
    line_fulfilled_1, _, user, run_key = lines_fulfilled
    assert list(Line.for_user_bootcamp_run(user, run_key)) == [line_fulfilled_1]


def test_total_paid_for_bootcamp_run(lines_fulfilled):
    """
    Test for the total_paid_for_bootcamp_run classmethod
    """
    line_fulfilled_1, _, user, run_key = lines_fulfilled
    assert Line.total_paid_for_bootcamp_run(user, run_key).get('total') == line_fulfilled_1.price
