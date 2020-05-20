""" Task helper functions for ecommerce """
import logging

from django.conf import settings

from applications.models import BootcampApplication
from hubspot import tasks


log = logging.getLogger(__name__)


def sync_hubspot_user(user):
    """
    Trigger celery task to sync a Profile to Hubspot

    Args:
        profile (Profile): The profile to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_contact_with_hubspot.delay(user.id)


def sync_hubspot_deal(application):
    """
    Trigger celery task to sync a deal to Hubspot

    Args:
        application (BootcampApplication): The BootcampApplication to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_deal_with_hubspot.delay(application.id)
        tasks.sync_line_with_hubspot.delay(application.id)


def sync_hubspot_deal_from_order(order):
    """
    Trigger celery task to sync a deal from an order to Hubspot

    Args:
        order (Order): The order to sync
    """
    try:
        sync_hubspot_deal(order.application)
    except BootcampApplication.DoesNotExist:
        log.error("No matching BootcampApplication found for order %s", order.id)


def sync_hubspot_product(bootcamp):
    """
    Trigger celery task to sync a Bootcamp to Hubspot

    Args:
        bootcamp (Bootcamp): The Bootcamp to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_product_with_hubspot.delay(bootcamp.id)
