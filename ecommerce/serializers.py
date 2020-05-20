"""Serializers for ecommerce"""
from rest_framework import serializers

from applications.models import BootcampApplication
from ecommerce.models import Order, Line
from klasses.serializers import BootcampRunSerializer, InstallmentSerializer


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for payment API, used to do basic validation.
    """
    payment_amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    run_key = serializers.IntegerField()


class OrderPartialSerializer(serializers.ModelSerializer):
    """
    Serializer for Order
    """
    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'created_on',
            'updated_on',
        )


class ApplicationOrderSerializer(serializers.ModelSerializer):
    """Serializer for orders that are part of a bootcamp application"""
    total_price_paid = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price_paid",
            "created_on",
            "updated_on",
        ]


class LineSerializer(serializers.ModelSerializer):
    """
    Serializer for Line
    """
    order = OrderPartialSerializer(read_only=True)
    price = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = Line
        fields = (
            'order',
            'run_key',
            'price',
            'description',
        )


class CheckoutDataSerializer(serializers.ModelSerializer):
    """Serializer for ecommerce information for a BootcampApplication"""
    bootcamp_run = BootcampRunSerializer()
    total_price = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True, source="price")
    total_paid = serializers.DecimalField(max_digits=20, decimal_places=2, read_only=True)
    payments = serializers.SerializerMethodField()
    installments = serializers.SerializerMethodField()

    def get_payments(self, application):
        """Serialized payments made by the user"""
        return LineSerializer(
            (order.line_set.first() for order in application.orders.all() if order.status == Order.FULFILLED),
            many=True,
        ).data

    def get_installments(self, application):
        """Installments with prices and due dates"""
        return InstallmentSerializer(
            application.bootcamp_run.installment_set.order_by('deadline'),
            many=True,
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
