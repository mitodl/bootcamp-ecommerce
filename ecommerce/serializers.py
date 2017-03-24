"""Serializers for ecommerce"""
from rest_framework.serializers import (
    DecimalField,
    IntegerField,
    Serializer,
)


class PaymentSerializer(Serializer):
    """
    Serializer for payment API, used to do basic validation.
    """
    total = DecimalField(max_digits=20, decimal_places=2, min_value=0.01)
    klass_id = IntegerField()
