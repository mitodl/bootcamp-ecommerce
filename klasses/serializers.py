"""
Serializers for klasses
"""
from rest_framework import serializers

from klasses.models import Installment


class InstallmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Installment.
    """

    class Meta:
        model = Installment
        fields = (
            'amount',
            'deadline',
        )
