"""Serializers for ecommerce"""
from decimal import Decimal
from rest_framework import serializers

from applications.models import BootcampApplication
from ecommerce.api import get_total_paid
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
    total_price = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()
    installments = serializers.SerializerMethodField()

    def get_total_price(self, application):
        """The personal price for the user, or the full price for the run"""
        return application.bootcamp_run.personal_price(application.user) or Decimal(0)

    def get_total_paid(self, application):
        """The total paid by the user for this application so far"""
        return get_total_paid(
            user=application.user,
            application_id=application.id,
            run_key=application.bootcamp_run.run_key,
        )

    def get_payments(self, application):
        """Serialized payments made by the user"""
        return LineSerializer(
            Line.objects.filter(order__application=application, order__status=Order.FULFILLED),
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
