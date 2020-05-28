"""
Serializers for bootcamps
"""
from rest_framework import serializers

from cms.serializers import BootcampRunPageSerializer
from klasses.models import Bootcamp, BootcampRun, Installment


class BootcampSerializer(serializers.ModelSerializer):
    """Serializer for Bootcamp model"""

    class Meta:
        model = Bootcamp
        fields = ["id", "title"]


class BootcampRunSerializer(serializers.ModelSerializer):
    """Serializer for BootcampRun model"""

    bootcamp = BootcampSerializer()

    def to_representation(self, instance):
        page_fields = {}
        if self.context.get("include_page") is True:
            page_fields = {
                "page": (
                    BootcampRunPageSerializer(instance=instance.bootcamprunpage).data
                    if hasattr(instance, "bootcamprunpage")
                    else {}
                )
            }
        return {**super().to_representation(instance), **page_fields}

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
        fields = ("amount", "deadline")
