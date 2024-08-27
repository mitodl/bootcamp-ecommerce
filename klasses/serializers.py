"""
Serializers for bootcamps
"""

from rest_framework import serializers

from cms.serializers import BootcampRunPageSerializer
from klasses.models import Bootcamp, BootcampRun, BootcampRunEnrollment, Installment


class InstallmentSerializer(serializers.ModelSerializer):
    """Serializer for Installment model"""

    amount = serializers.DecimalField(decimal_places=2, max_digits=20)

    class Meta:
        model = Installment
        fields = ("amount", "deadline")


class BootcampSerializer(serializers.ModelSerializer):
    """Serializer for Bootcamp model"""

    class Meta:
        model = Bootcamp
        fields = ["id", "title", "readable_id"]


class BootcampRunSerializer(serializers.ModelSerializer):
    """Serializer for BootcampRun model"""

    bootcamp = BootcampSerializer()
    installments = InstallmentSerializer(many=True, source="installment_set")

    def to_representation(self, instance):  # noqa: D102
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
            "novoed_course_stub",
            "start_date",
            "end_date",
            "early_bird_deadline",
            "is_payable",
            "installments",
            "bootcamp_run_id",
            "allows_skipped_steps",
        ]


class BootcampRunEnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for BootcampRunEnrollment model"""

    class Meta:
        model = BootcampRunEnrollment
        fields = ["id", "user_id", "bootcamp_run_id", "novoed_sync_date"]
