""" Task helper functions for ecommerce """
from django.conf import settings

from hubspot import tasks


def sync_hubspot_user(profile):
    """
    Trigger celery task to sync a Profile to Hubspot

    Args:
        profile (Profile): The profile to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_contact_with_hubspot.delay(profile.id)


def sync_hubspot_deal(klass):
    """
    Trigger celery task to sync an order to Hubspot if it has lines

    Args:
        order (Order): The order to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_deal_with_hubspot.delay(klass.id)


def sync_hubspot_product(bootcamp):
    """
    Trigger celery task to sync a Line to Hubspot

    Args:
        line (Line): The line to sync
    """
    if settings.HUBSPOT_API_KEY:
        tasks.sync_bootcamp_with_hubspot.delay(bootcamp.id)
