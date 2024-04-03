"""Serializers for ecommerce"""

from rest_framework import serializers

from applications.models import BootcampApplication
from ecommerce.models import Order, Line, Receipt
from klasses.serializers import BootcampRunSerializer, InstallmentSerializer


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for payment API, used to do basic validation.
    """

    payment_amount = serializers.DecimalField(
        max_digits=20, decimal_places=2, min_value=0.01
    )
    application_id = serializers.IntegerField()


class OrderPartialSerializer(serializers.ModelSerializer):
    """
    Serializer for Order
    """

    class Meta:
        model = Order
        fields = ("id", "status", "created_on", "updated_on")


class ReceiptSerializer(serializers.ModelSerializer):
    """Serializer for receipts for a user"""

    class Meta:
        model = Receipt
        fields = ["id", "payment_method"]


class ApplicationOrderSerializer(serializers.ModelSerializer):
    """Serializer for orders that are part of a bootcamp application"""

    total_price_paid = serializers.DecimalField(decimal_places=2, max_digits=20)
    payment_method = serializers.SerializerMethodField()

    def get_payment_method(self, order):
        """Get the payment method used in the last receipt for the order"""
        if order.payment_type == Order.CYBERSOURCE_TYPE:
            # There should only be one receipt for an order most of the time, but it's possible
            # there is a duplicate or a Cybersource error in one of the receipts.
            receipt = order.receipt_set.order_by("id").last()
            return receipt.payment_method if receipt is not None else None
        elif order.payment_type == Order.WIRE_TRANSFER_TYPE:
            return "Wire Transfer"

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price_paid",
            "created_on",
            "updated_on",
            "payment_method",
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""

    class Meta:
        model = Order
        fields = ["id", "status", "application_id", "created_on", "updated_on"]


class LineSerializer(serializers.ModelSerializer):
    """
    Serializer for Line
    """

    order = OrderPartialSerializer(read_only=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=20)
    run_key = serializers.SerializerMethodField()

    def get_run_key(self, line):
        """get run_key from bootcamp_run"""
        return line.bootcamp_run.run_key

    class Meta:
        model = Line
        fields = ("order", "price", "description", "run_key")


class CheckoutDataSerializer(serializers.ModelSerializer):
    """Serializer for ecommerce information for a BootcampApplication"""

    bootcamp_run = BootcampRunSerializer()
    total_price = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True, source="price"
    )
    total_paid = serializers.DecimalField(
        max_digits=20, decimal_places=2, read_only=True
    )
    payments = serializers.SerializerMethodField()
    installments = serializers.SerializerMethodField()

    def get_payments(self, application):
        """Serialized payments made by the user"""
        return LineSerializer(
            (
                order.line_set.first()
                for order in application.orders.all()
                if order.status == Order.FULFILLED
            ),
            many=True,
        ).data

    def get_installments(self, application):
        """Installments with prices and due dates"""
        return InstallmentSerializer(
            application.bootcamp_run.installment_set.order_by("deadline"), many=True
        ).data

    class Meta:
        model = BootcampApplication
        fields = [
            "id",
            "bootcamp_run",
            "total_price",
            "total_paid",
            "payments",
            "installments",
        ]
