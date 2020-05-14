"""Serializers for ecommerce"""
from rest_framework import serializers

from ecommerce.models import Order, Line


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
