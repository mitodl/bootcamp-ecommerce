"""
Hubspot tasks
"""
import logging
import re

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from bootcamp.celery import app

from hubspot.api import (
    send_hubspot_request,
    make_contact_sync_message,
    get_sync_errors,
    hubspot_timestamp,
    parse_hubspot_id,
    make_product_sync_message, make_deal_sync_message, make_line_sync_message, exists_in_hubspot)
from hubspot.models import HubspotErrorCheck, HubspotLineResync
from klasses.models import PersonalPrice

log = logging.getLogger()

HUBSPOT_SYNC_URL = "/extensions/ecomm/v1/sync-messages"
ASSOCIATED_DEAL_RE = re.compile(fr"\[hs_assoc__deal_id: (.+)\]")


@app.task
def sync_contact_with_hubspot(profile_id):
    """Send a sync-message to sync a user with a hubspot contact"""
    body = make_contact_sync_message(profile_id)
    if not body[0].get('propertyNameToValues', {}).get('email'):
        return  # Skip if message is missing required field

    response = send_hubspot_request("CONTACT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def sync_product_with_hubspot(bootcamp_id):
    """Send a sync-message to sync a Bootcamp with a hubspot product"""
    body = make_product_sync_message(bootcamp_id)
    response = send_hubspot_request("PRODUCT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def sync_deal_with_hubspot(personal_price_id):
    """Send a sync-message to sync a personal price with a hubspot deal"""
    body = make_deal_sync_message(personal_price_id)
    response = send_hubspot_request("DEAL", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def sync_line_with_hubspot(personal_price_id):
    """Send a sync-message to sync a personal price with a hubspot line"""
    body = make_line_sync_message(personal_price_id)
    response = send_hubspot_request("LINE_ITEM", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def check_hubspot_api_errors():
    """Check for and log any errors that occurred since the last time this was run"""
    if not settings.HUBSPOT_API_KEY:
        return
    curr_time = timezone.now()
    last_check, _ = HubspotErrorCheck.objects.get_or_create(
        defaults={"checked_on": curr_time}
    )
    last_timestamp = hubspot_timestamp(last_check.checked_on)

    for error in get_sync_errors():
        error_timestamp = error.get("errorTimestamp")
        if error_timestamp > last_timestamp:
            obj_type = (error.get("objectType", "N/A"),)
            obj_id = parse_hubspot_id(error.get("integratorObjectId", ""))
            error_type = error.get("type", "N/A")
            details = error.get("details", "")

            if (
                obj_id is not None and
                "LINE_ITEM" in obj_type and
                error_type == "INVALID_ASSOCIATION_PROPERTY" and
                ASSOCIATED_DEAL_RE.search(details) is not None
            ):
                try:
                    personal_price = PersonalPrice.objects.get(id=obj_id)
                except ObjectDoesNotExist:
                    pass
                else:
                    HubspotLineResync.objects.get_or_create(personal_price=personal_price)
                    continue

            log.error(
                "Hubspot error %s for %s id %s: %s",
                error_type,
                obj_type,
                str(obj_id),
                details,
            )
        else:
            break

    retry_invalid_line_associations()
    last_check.checked_on = curr_time
    last_check.save()


def retry_invalid_line_associations():
    """
    Check lines that have errored and retry them if their orders have synced
    """
    for hubspot_line_resync in HubspotLineResync.objects.all():
        if exists_in_hubspot("LINE_ITEM", hubspot_line_resync.personal_price.id):
            hubspot_line_resync.delete()
            continue

        if exists_in_hubspot("DEAL", hubspot_line_resync.personal_price.id):
            sync_line_with_hubspot(hubspot_line_resync.personal_price.id)
