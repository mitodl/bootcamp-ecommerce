"""
Serializers for bootcamps
"""
from rest_framework import serializers

from klasses.models import Bootcamp, BootcampRun, Installment


class BootcampSerializer(serializers.ModelSerializer):
    """Serializer for Bootcamp model"""
    class Meta:
        model = Bootcamp
        fields = [
            "id",
            "title",
        ]


class BootcampRunSerializer(serializers.ModelSerializer):
    """Serializer for BootcampRun model"""
    bootcamp = BootcampSerializer()

    class Meta:
        model = BootcampRun
        fields = [
            "id",
            "display_title",
            "bootcamp",
            "title",
            "run_key",
            "start_date",
            "end_date",
        ]


class InstallmentSerializer(serializers.ModelSerializer):
    """Serializer for Installment model"""
    amount = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = Installment
        fields = (
            'amount',
            'deadline',
        )
