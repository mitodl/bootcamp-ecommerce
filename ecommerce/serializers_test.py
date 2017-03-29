"""Tests for serializers"""
from unittest import TestCase

from ddt import (
    data,
    ddt,
    unpack,
)

from ecommerce.serializers import PaymentSerializer


@ddt
class PaymentSerializersTests(TestCase):
    """Tests for payment serializers"""

    @data(
        [{"total": "345", "klass_id": 3}, True],
        [{"total": "-3", "klass_id": 3}, False],
        [{"total": "345"}, False],
        [{"klass_id": "345"}, False],
    )
    @unpack
    def test_validation(self, payload, is_valid):
        """
        Assert that validation is turned on for the things we care about
        """
        assert is_valid == PaymentSerializer(data=payload).is_valid()
