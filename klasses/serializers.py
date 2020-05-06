"""
Serializers for bootcamps
"""
from rest_framework import serializers

from klasses.models import Installment


class InstallmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Installment.
    """
    amount = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = Installment
        fields = (
            'amount',
            'deadline',
        )
