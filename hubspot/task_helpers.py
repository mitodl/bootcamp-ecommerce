""" Task helper functions for ecommerce """
from django.conf import settings

from ecommerce.models import Order
from hubspot import tasks
from klasses.models import PersonalPrice


def sync_hubspot_user(profile):
    """
    Trigger celery task to sync a Profile to Hubspot

    Args:
        profile (Profile): The profile to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_contact_with_hubspot.delay(profile.id)


def sync_hubspot_deal(personal_price):
    """
    Trigger celery task to sync a deal to Hubspot

    Args:
        personal_price (PersonalPrice): The PersonalPrice to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_deal_with_hubspot.delay(personal_price.id)
        tasks.sync_line_with_hubspot.delay(personal_price.id)


def sync_hubspot_deal_from_order(order):
    """
    Trigger celery task to sync a deal from an order to Hubspot

    Args:
        order (Order): The order to sync
    """

    if not isinstance(order, Order):
        # Some tests cause order to be a string.
        return

    try:
        personal_price = PersonalPrice.objects.get(
            user=order.user,
            klass=order.get_klass()  # Under tha assumption that its one klass per order
        )
        sync_hubspot_deal(personal_price)
    except PersonalPrice.DoesNotExist:
        pass


def sync_hubspot_product(bootcamp):
    """
    Trigger celery task to sync a Bootcamp to Hubspot

    Args:
        bootcamp (Bootcamp): The Bootcamp to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_product_with_hubspot.delay(bootcamp.id)
