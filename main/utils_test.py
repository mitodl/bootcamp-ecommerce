"""
Tests for the utils module
"""
import unittest
from math import ceil

from django.test import (
    override_settings,
    TestCase,
)

from ecommerce.factories import (
    Order,
    ReceiptFactory,
)
from main.utils import (
    get_field_names,
    serialize_model_object,
    chunks,
)


def format_as_iso8601(time, remove_microseconds=True):
    """Helper function to format datetime with the Z at the end"""
    # Can't use datetime.isoformat() because format is slightly different from this
    iso_format = '%Y-%m-%dT%H:%M:%S.%f'
    # chop off microseconds to make milliseconds
    str_time = time.strftime(iso_format)
    if remove_microseconds:
        str_time = str_time[:-3]
    return str_time + "Z"


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


class UtilTests(unittest.TestCase):
    """
    Tests for assorted utility functions
    """

    def test_chunks(self):
        """
        test for chunks
        """
        input_list = list(range(113))
        output_list = []
        for nums in chunks(input_list):
            output_list += nums
        assert output_list == input_list

        output_list = []
        for nums in chunks(input_list, chunk_size=1):
            output_list += nums
        assert output_list == input_list

        output_list = []
        for nums in chunks(input_list, chunk_size=124):
            output_list += nums
        assert output_list == input_list

    def test_chunks_iterable(self):
        """
        test that chunks works on non-list iterables too
        """
        count = 113
        input_range = range(count)
        chunk_output = []
        for chunk in chunks(input_range, chunk_size=10):
            chunk_output.append(chunk)
        assert len(chunk_output) == ceil(113/10)

        range_list = []
        for chunk in chunk_output:
            range_list += chunk
        assert range_list == list(range(count))
