"""
Serializers for hubspot_sync
"""
import logging
from decimal import Decimal


from mitol.hubspot_api.api import format_app_id
from rest_framework import serializers

from applications.api import get_required_submission_type
from applications.constants import AppStates, SUBMISSION_TYPE_STATE
from applications.models import BootcampApplication, BootcampApplicationLine
from ecommerce.models import Order
from hubspot_sync.constants import HUBSPOT_DEAL_PREFIX
from klasses.models import BootcampRun
from main import settings

log = logging.getLogger(__name__)


class UniqueAppIdMixin(serializers.Serializer):
    """Unique App ID field for Hubspot serializers"""

    unique_app_id = serializers.SerializerMethodField()

    def get_unique_app_id(self, instance):
        """Get the app_id for the object"""
        return format_app_id(instance.id)


class HubspotProductSerializer(serializers.ModelSerializer, UniqueAppIdMixin):
    """
    Serializer for turning a BootcampRun into a hubspot_sync Product
    """

    name = serializers.CharField(source="title")

    class Meta:
        model = BootcampRun
        fields = ["name", "bootcamp_run_id", "unique_app_id"]


class HubspotDealSerializer(serializers.ModelSerializer, UniqueAppIdMixin):
    """
    Serializer for turning a BootcampApplication into a hubspot_sync deal.
    """

    dealname = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    bootcamp_name = serializers.SerializerMethodField()
    application_stage = serializers.SerializerMethodField()
    pipeline = serializers.ReadOnlyField(default=settings.HUBSPOT_PIPELINE_ID)

    def get_dealname(self, instance):
        """Get a formatted name for the deal"""
        return f"{HUBSPOT_DEAL_PREFIX}-{instance.id}"

    def get_amount(self, instance):
        """Get a string of the price"""
        price = instance.bootcamp_run.personal_price(instance.user)
        if price:
            return price.to_eng_string()
        return "0.00"

    def get_bootcamp_name(self, instance):
        """Get the name of the bootcamp run"""
        return instance.bootcamp_run.title

    def get_application_stage(self, instance):
        """Get the application stage"""
        state = instance.state
        if state == AppStates.AWAITING_USER_SUBMISSIONS.value:
            next_step = get_required_submission_type(instance)
            if next_step:
                state = SUBMISSION_TYPE_STATE.get(next_step, state)
        return state

    def to_representation(self, instance):
        # Populate deal data
        data = super().to_representation(instance)
        orders = Order.objects.filter(
            user=instance.user, line__bootcamp_run_id=instance.bootcamp_run.id
        )
        if orders.exists():
            amount_paid = Decimal(0)
            has_refunds = False
            for order in orders:
                if order.status == Order.FULFILLED:
                    if order.total_price_paid < 0:
                        has_refunds = True
                    amount_paid += order.total_price_paid

            data["total_price_paid"] = amount_paid.to_eng_string()
            if amount_paid >= instance.bootcamp_run.personal_price(instance.user):
                data["dealstage"] = "shipped"
            elif amount_paid > 0 or has_refunds:
                data["dealstage"] = "processed"
            else:
                data["dealstage"] = "checkout_completed"
        else:
            data["dealstage"] = "checkout_pending"

        return data

    class Meta:
        model = BootcampApplication
        fields = [
            "dealname",
            "amount",
            "application_stage",
            "bootcamp_name",
            "unique_app_id",
            "pipeline",
        ]


class HubspotLineSerializer(serializers.ModelSerializer, UniqueAppIdMixin):
    """
    Serializer for turning a BootcampApplication into a hubspot line item
    """

    name = serializers.SerializerMethodField()
    hs_product_id = serializers.SerializerMethodField()
    quantity = serializers.CharField(default="1")

    def get_name(self, instance):
        """Get the product version name"""
        return instance.application.bootcamp_run.title

    def get_hs_product_id(self, instance):
        """Return the hubspot id for the product"""
        from hubspot_sync.api import get_hubspot_id_for_object

        return get_hubspot_id_for_object(instance.application.bootcamp_run)

    class Meta:
        model = BootcampApplicationLine
        fields = ["name", "hs_product_id", "unique_app_id", "quantity"]
