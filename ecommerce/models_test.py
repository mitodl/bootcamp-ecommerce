"""
Tests for ecommerce models
"""
from django.test import (
    override_settings,
    TestCase,
)

from bootcamp.utils import serialize_model_object
from ecommerce.factories import (
    LineFactory,
    OrderFactory,
    ReceiptFactory,
)
from ecommerce.models import Order, Line
from klasses.factories import KlassFactory
from klasses.models import Klass


@override_settings(CYBERSOURCE_SECURITY_KEY='fake')
class OrderTests(TestCase):
    """
    Tests for Order, Line, and Receipt
    """

    def test_order_str(self):
        """Test Order.__str__"""
        order = LineFactory.create().order
        assert str(order) == "Order {}, status={} for user={}".format(order.id, order.status, order.user)

    def test_line_str(self):
        """Test Line.__str__"""
        line = LineFactory.create()
        assert str(line) == (
            "Line for {order}, price={price}, klass_id={klass_id}, description={description}".format(
                order=line.order,
                klass_id=line.klass_id,
                price=line.price,
                description=line.description,
            )
        )

    def test_receipt_str_with_order(self):
        """Test Receipt.__str__ with an order"""
        receipt = ReceiptFactory.create()
        assert str(receipt) == "Receipt for order {}".format(receipt.order.id if receipt.order else None)

    def test_receipt_str_no_order(self):
        """Test Receipt.__str__ with no order"""
        receipt = ReceiptFactory.create(order=None)
        assert str(receipt) == "Receipt with no attached order"

    def test_to_dict(self):
        """
        Test Order.to_dict()
        """
        order = OrderFactory.create()
        lines = [LineFactory.create(order=order) for _ in range(5)]
        data = order.to_dict()
        lines_data = data.pop('lines')
        assert serialize_model_object(order) == data
        assert lines_data == [serialize_model_object(line) for line in lines]


class LineDescriptionTests(TestCase):
    """
    Tests for Order.line_description
    """
    def test_empty(self):
        """If there is no Line there should be an empty string"""
        order = OrderFactory.create()
        assert order.line_description == ""

    def test_description(self):
        """line_description should be line.description of the first line"""
        line = LineFactory.create()
        # Second line should be ignored
        LineFactory.create(order=line.order)
        assert line.order.line_description == line.description


class KlassTitleTests(TestCase):
    """Tests for Order.klass_title"""

    def test_empty(self):
        """If there is no Line there should be an empty string"""
        order = OrderFactory.create()
        assert order.klass_title == ""

    def test_no_klass(self):
        """If there is no Klass there should be an empty string"""
        line = LineFactory.create()
        assert Klass.objects.filter(klass_id=line.klass_id).exists() is False
        assert line.order.klass_title == ""

    def test_klass_title(self):
        """klass_title should be klass.title for the given klass_id"""
        klass = KlassFactory.create()
        line = LineFactory.create(klass_id=klass.klass_id)
        assert line.order.klass_title == klass.title


class LineTest(TestCase):
    """
    Tests for Line helper classmethods
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.order_fulfilled_1 = OrderFactory.create(status=Order.FULFILLED)
        cls.line_fulfilled_1 = LineFactory.create(order=cls.order_fulfilled_1)
        cls.user = cls.order_fulfilled_1.user
        cls.klass_id = cls.line_fulfilled_1.klass_id
        cls.order_fulfilled_2 = OrderFactory.create(user=cls.user, status=Order.FULFILLED)
        cls.line_fulfilled_2 = LineFactory.create(order=cls.order_fulfilled_2)
        cls.order_created = OrderFactory.create(user=cls.user, status=Order.CREATED)
        cls.line_created = LineFactory.create(order=cls.order_created, klass_id=cls.klass_id)

    def test_fulfilled_for_user(self):
        """
        Test for the fulfilled_for_user classmethod
        """
        assert list(Line.fulfilled_for_user(self.user)) == sorted(
            [self.line_fulfilled_1, self.line_fulfilled_2], key=lambda x: x.klass_id)

    def test_for_user_klass(self):
        """
        Test for the for_user_klass classmethod
        """
        assert list(Line.for_user_klass(self.user, self.klass_id)) == [self.line_fulfilled_1]

    def test_total_paid_for_klass(self):
        """
        Test for the total_paid_for_klass classmethod
        """
        assert Line.total_paid_for_klass(self.user, self.klass_id).get('total') == self.line_fulfilled_1.price
