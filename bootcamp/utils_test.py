"""
Tests for the utils module
"""
import unittest

from django.test import (
    override_settings,
    TestCase,
)

from ecommerce.factories import (
    Order,
    ReceiptFactory,
)
from bootcamp.utils import (
    get_field_names,
    serialize_model_object,
)


def format_as_iso8601(time):
    """Helper function to format datetime with the Z at the end"""
    # Can't use datetime.isoformat() because format is slightly different from this
    iso_format = '%Y-%m-%dT%H:%M:%S.%f'
    # chop off microseconds to make milliseconds
    return time.strftime(iso_format)[:-3] + "Z"


class SerializerTests(TestCase):
    """
    Tests for serialize_model
    """
    def test_jsonfield(self):
        """
        Test a model with a JSONField is handled correctly
        """
        with override_settings(CYBERSOURCE_SECURITY_KEY='asdf'):
            receipt = ReceiptFactory.create()
            assert serialize_model_object(receipt) == {
                'created_on': format_as_iso8601(receipt.created_on),
                'data': receipt.data,
                'id': receipt.id,
                'updated_on': format_as_iso8601(receipt.updated_on),
                'order': receipt.order.id,
            }


class FieldNamesTests(unittest.TestCase):
    """
    Tests for get_field_names
    """

    def test_get_field_names(self):
        """
        Assert that get_field_names does not include related fields
        """
        assert set(get_field_names(Order)) == {
            'user',
            'status',
            'total_price_paid',
            'created_on',
            'updated_on',
        }
