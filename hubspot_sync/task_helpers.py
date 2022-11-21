""" Task helper functions for hubspot_sync """
import logging

from django.conf import settings

from hubspot_sync import tasks

log = logging.getLogger(__name__)


def sync_hubspot_user(user):
    """
    Trigger celery task to sync a Profile to Hubspot

    Args:
        profile (Profile): The profile to sync
    """
    if settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN:
        tasks.sync_contact_with_hubspot.delay(user.id)


def sync_hubspot_application(application):
    """
    Trigger celery task to sync a deal to Hubspot

    Args:
        application (BootcampApplication): The BootcampApplication to sync
    """
    if settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN:
        tasks.sync_deal_with_hubspot.delay(application.id)


def sync_hubspot_application_from_order(order):
    """
    Trigger celery task to sync a deal from an order to Hubspot

    Args:
        order (Order): The order to sync
    """
    try:
        sync_hubspot_application(order.application)
    except AttributeError:
        log.error("No matching BootcampApplication found for order %s", order.id)


def sync_hubspot_product(bootcamp_run):
    """
    Trigger celery task to sync a Bootcamp to Hubspot

    Args:
        bootcamp_run (BootcampRun): The BootcampRun to sync
    """
    if settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN:
        tasks.sync_product_with_hubspot.delay(bootcamp_run.id)
