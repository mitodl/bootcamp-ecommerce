"""
Serializers for hubspot
"""
import logging
from decimal import Decimal

from rest_framework import serializers

from applications.models import BootcampApplication
from ecommerce.models import Order
from klasses.models import Bootcamp

log = logging.getLogger(__name__)


class HubspotProductSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a Bootcamp into a hubspot Product
    """
    class Meta:
        model = Bootcamp
        fields = ['title']


class HubspotDealSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a BootcampApplication into a hubspot deal.
    """
    name = serializers.SerializerMethodField()
    purchaser = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    bootcamp_name = serializers.SerializerMethodField()
    application_stage = serializers.CharField(source="state")

    def get_name(self, instance):
        """Get a formatted name for the deal"""
        return f"Bootcamp-application-order-{instance.id}"

    def get_purchaser(self, instance):
        """Get the id of the associated user"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.user.profile.id)

    def get_price(self, instance):
        """Get a string of the price"""
        return instance.bootcamp_run.personal_price(instance.user).to_eng_string()

    def get_bootcamp_name(self, instance):
        """Get the name of the bootcamp"""
        return instance.bootcamp_run.bootcamp.title

    def to_representation(self, instance):
        # Populate order data
        data = super().to_representation(instance)
        orders = Order.objects.filter(user=instance.user, line__run_key=instance.bootcamp_run.run_key)
        if orders.exists():
            amount_paid = Decimal(0)
            for order in orders:
                if order.status == Order.FULFILLED:
                    amount_paid += order.total_price_paid

            data['total_price_paid'] = amount_paid.to_eng_string()
            if amount_paid >= instance.bootcamp_run.personal_price(instance.user):
                data['status'] = 'shipped'
            elif amount_paid > 0:
                data['status'] = 'processed'
            else:
                data['status'] = 'checkout_completed'
        else:
            data['status'] = 'checkout_pending'

        return data

    class Meta:
        model = BootcampApplication
        fields = ['name', 'price', 'application_stage', 'purchaser', 'bootcamp_name']


class HubspotLineSerializer(serializers.ModelSerializer):
    """
    Serializer for turning a BootcampApplication into a hubspot line item
    """
    order = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    def get_order(self, instance):
        """Get the id of the associated deal"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.integration_id)

    def get_product(self, instance):
        """Get the id of the associated Bootcamp"""
        from hubspot.api import format_hubspot_id
        return format_hubspot_id(instance.bootcamp_run.bootcamp.id)

    class Meta:
        model = BootcampApplication
        fields = ['order', 'product']
