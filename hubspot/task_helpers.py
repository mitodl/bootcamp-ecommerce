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
