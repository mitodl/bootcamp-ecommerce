"""Tests for serializers"""
import pytest

from main.test_utils import format_as_iso8601
from ecommerce.factories import LineFactory
from ecommerce.serializers import (
    PaymentSerializer,
    OrderPartialSerializer,
    LineSerializer,
)


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
        'created_on': format_as_iso8601(line.order.created_on, remove_microseconds=False),
        'updated_on': format_as_iso8601(line.order.updated_on, remove_microseconds=False),
    }
    assert OrderPartialSerializer(line.order).data == expected


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
            'created_on': format_as_iso8601(line.order.created_on, remove_microseconds=False),
            'updated_on': format_as_iso8601(line.order.updated_on, remove_microseconds=False),
        }
    }

    assert LineSerializer(line).data == expected
