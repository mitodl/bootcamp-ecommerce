"""Tests for Bootcamp models"""
from django.test import TestCase

from main.utils import serialize_model_object
from ecommerce.factories import (
    LineFactory,
    OrderFactory,
)
from ecommerce.models import (
    OrderAudit,
)
from profiles.factories import UserFactory


class ModelsTests(TestCase):
    """Tests for abstract models"""

    def test_save_and_log(self):
        """
        Tests that save_and_log() creates an audit record with the correct information.
        """
        acting_user = UserFactory.create()
        order = OrderFactory.create()
        original_before_json = serialize_model_object(order)
        original_before_json['lines'] = []
        # Make sure audit object is created
        assert OrderAudit.objects.count() == 0
        order.save_and_log(acting_user)
        assert OrderAudit.objects.count() == 1
        # Make sure the before and after data are correct
        original_after_json = serialize_model_object(order)
        original_after_json['lines'] = []
        audit = OrderAudit.objects.first()
        before_json = audit.data_before
        after_json = audit.data_after
        for field, value in before_json.items():
            # Data before
            if isinstance(value, float):
                # JSON serialization of FloatField is precise, so we need to do almost equal
                self.assertAlmostEqual(value, original_before_json[field])
            else:
                assert value == original_before_json[field]
        for field, value in after_json.items():
            # Data after
            if isinstance(value, float):
                # JSON serialization of FloatField is precise, so we need to do almost equal
                self.assertAlmostEqual(value, original_after_json[field])
            else:
                assert value == original_after_json[field]

    def test_to_dict(self):
        """
        assert output of to_dict
        """
        line = LineFactory.create()
        order = line.order
        order_dict = order.to_dict()
        del order_dict['lines']
        assert order_dict == serialize_model_object(order)

        lines_dict = order.to_dict()['lines']
        assert lines_dict == [serialize_model_object(line)]
