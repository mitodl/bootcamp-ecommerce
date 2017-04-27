"""Serializers for ecommerce"""
from rest_framework import serializers

from ecommerce.models import Order, Line


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for payment API, used to do basic validation.
    """
    payment_amount = serializers.DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    klass_id = serializers.IntegerField()


class OrderPartialSerializer(serializers.ModelSerializer):
    """
    Serializer for Order
    """
    class Meta:
        model = Order
        fields = (
            'status',
            'created_on',
            'updated_on',
        )


class LineSerializer(serializers.ModelSerializer):
    """
    Serializer for Line
    """
    order = OrderPartialSerializer(read_only=True)

    class Meta:
        model = Line
        fields = (
            'order',
            'klass_id',
            'description',
        )
