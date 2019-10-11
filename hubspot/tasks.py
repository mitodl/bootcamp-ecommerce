"""
Hubspot tasks
"""
import logging
import re

from django.conf import settings
from django.utils import timezone

from bootcamp.celery import app

from hubspot.api import (
    send_hubspot_request,
    make_contact_sync_message,
    get_sync_errors,
    hubspot_timestamp,
    parse_hubspot_id,
    make_product_sync_message, make_deal_sync_message)
from hubspot.models import HubspotErrorCheck


log = logging.getLogger()

HUBSPOT_SYNC_URL = "/extensions/ecomm/v1/sync-messages"
ASSOCIATED_DEAL_RE = re.compile(fr"\[hs_assoc__deal_id: (.+)\]")


@app.task
def sync_contact_with_hubspot(profile_id):
    """Send a sync-message to sync a user with a hubspot contact"""
    body = make_contact_sync_message(profile_id)
    response = send_hubspot_request("CONTACT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()

@app.task
def sync_product_with_hubspot(bootcamp_id):
    """Send a sync-message to sync a user with a hubspot product"""
    body = make_product_sync_message(bootcamp_id)
    response = send_hubspot_request("PRODUCT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()

@app.task
def sync_deal_with_hubspot(klass_id):
    """Send a sync-message to sync a user with a hubspot deal"""
    body = make_deal_sync_message(klass_id)
    response = send_hubspot_request("DEAL", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def check_hubspot_api_errors():
    """Check for and log any errors that occurred since the last time this was run"""
    if not settings.HUBSPOT_API_KEY:
        return
    last_check, _ = HubspotErrorCheck.objects.get_or_create(
        defaults={"checked_on": timezone.now()}
    )
    last_timestamp = hubspot_timestamp(last_check.checked_on)

    for error in get_sync_errors():
        error_timestamp = error.get("errorTimestamp")
        if error_timestamp > last_timestamp:
            obj_type = (error.get("objectType", "N/A"),)
            obj_id = parse_hubspot_id(error.get("integratorObjectId", ""))
            error_type = error.get("type", "N/A")
            details = error.get("details", "")

            log.error(
                "Hubspot error %s for %s id %s: %s",
                error_type,
                obj_type,
                str(obj_id),
                details,
            )
        else:
            break

    last_check.checked_on = timezone.now()
    last_check.save()
