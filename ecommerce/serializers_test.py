"""Tests for serializers"""
from unittest import TestCase

from ddt import (
    data,
    ddt,
    unpack,
)
from django.test import TestCase as DjangoTestCase

from main.test_utils import format_as_iso8601
from ecommerce.factories import LineFactory
from ecommerce.serializers import (
    PaymentSerializer,
    OrderPartialSerializer,
    LineSerializer,
)


@ddt
class PaymentSerializersTests(TestCase):
    """Tests for payment serializers"""

    @data(
        [{"payment_amount": "345", "run_key": 3}, True],
        [{"payment_amount": "-3", "run_key": 3}, False],
        [{"payment_amount": "345"}, False],
        [{"run_key": "345"}, False],
    )
    @unpack
    def test_validation(self, payload, is_valid):
        """
        Assert that validation is turned on for the things we care about
        """
        assert is_valid == PaymentSerializer(data=payload).is_valid()


class LineOrderSerializerTests(DjangoTestCase):
    """
    Tests for Line and Order serializers
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.line = LineFactory.create()

    def test_orderpartial_serializer(self):
        """
        Test order partial serializer result
        """
        expected = {
            'id': self.line.order.id,
            'status': self.line.order.status,
            'created_on': format_as_iso8601(self.line.order.created_on, remove_microseconds=False),
            'updated_on': format_as_iso8601(self.line.order.updated_on, remove_microseconds=False),
        }
        assert OrderPartialSerializer(self.line.order).data == expected

    def test_line_serializer(self):
        """
        Test for line serializer result
        """
        expected = {
            'run_key': self.line.run_key,
            'description': self.line.description,
            'price': self.line.price,
            'order': {
                'id': self.line.order.id,
                'status': self.line.order.status,
                'created_on': format_as_iso8601(self.line.order.created_on, remove_microseconds=False),
                'updated_on': format_as_iso8601(self.line.order.updated_on, remove_microseconds=False),
            }
        }

        assert LineSerializer(self.line).data == expected
