"""
Hubspot tasks
"""
import logging
import re

import celery
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from requests import HTTPError

from applications.models import BootcampApplication
from main.celery import app

from hubspot.api import (
    send_hubspot_request,
    make_contact_sync_message,
    get_sync_errors,
    hubspot_timestamp,
    parse_hubspot_deal_id,
    make_product_sync_message,
    make_deal_sync_message,
    make_line_sync_message,
    exists_in_hubspot,
)
from hubspot.models import HubspotErrorCheck, HubspotLineResync

log = logging.getLogger(__name__)

HUBSPOT_SYNC_URL = "/extensions/ecomm/v1/sync-messages"
ASSOCIATED_DEAL_RE = re.compile(r"\[hs_assoc__deal_id: (.+)\]")


@app.task
def sync_contact_with_hubspot(user_id):
    """Send a sync-message to sync a user with a hubspot contact"""
    body = make_contact_sync_message(user_id)
    if not body[0].get("propertyNameToValues", {}).get("email"):
        return  # Skip if message is missing required field

    response = send_hubspot_request("CONTACT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def sync_product_with_hubspot(bootcamp_run_id):
    """Send a sync-message to sync a BootcampRun with a hubspot product"""
    body = make_product_sync_message(bootcamp_run_id)
    response = send_hubspot_request("PRODUCT", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task(
    autoretry_for=(ObjectDoesNotExist,), retry_kwargs={"max_retries": 3, "countdown": 5}
)
def sync_application_with_hubspot(application_id):
    """Sync the application to a hubspot deal and line"""
    tasks = [
        sync_deal_with_hubspot.si(application_id),
        sync_line_with_hubspot.si(application_id),
    ]
    return celery.chain(tasks)()


@app.task
def sync_deal_with_hubspot(application_id):
    """Send a sync-message to sync a personal price with a hubspot deal"""
    body = make_deal_sync_message(application_id)
    response = send_hubspot_request("DEAL", HUBSPOT_SYNC_URL, "PUT", body=body)
    response.raise_for_status()


@app.task
def sync_line_with_hubspot(application_id):
    """Send a sync-message to sync a personal price with a hubspot line"""
    body = make_line_sync_message(application_id)
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
            obj_id = parse_hubspot_deal_id(error.get("integratorObjectId", ""))
            error_type = error.get("type", "N/A")
            details = error.get("details", "")

            if (
                obj_id is not None
                and "LINE_ITEM" in obj_type
                and error_type == "INVALID_ASSOCIATION_PROPERTY"
                and ASSOCIATED_DEAL_RE.search(details) is not None
            ):
                try:
                    application = BootcampApplication.objects.get(id=obj_id)
                except ObjectDoesNotExist:
                    pass
                else:
                    HubspotLineResync.objects.get_or_create(application=application)
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
        if exists_in_hubspot(
            "LINE_ITEM", hubspot_line_resync.application.integration_id
        ):
            hubspot_line_resync.delete()
            continue

        if exists_in_hubspot("DEAL", hubspot_line_resync.application.integration_id):
            sync_line_with_hubspot(hubspot_line_resync.application.id)
        else:
            sync_application_with_hubspot(hubspot_line_resync.application.id)


def sync_bulk_with_hubspot(
    objects, make_object_sync_message, object_type, print_to_console=False, **kwargs
):
    """
    Sync all database objects of a certain type with hubspot
    Args:
        objects (iterable) objects to sync
        make_object_sync_message (function) function that takes an objectID and
            returns a sync message for that model
        object_type (str) one of "CONTACT", "DEAL", "PRODUCT", "LINE_ITEM"
        print_to_console (bool) whether to print status messages to console
    """
    sync_messages = [make_object_sync_message(obj.id, **kwargs)[0] for obj in objects]

    if object_type == "CONTACT":
        # Skip sync if message is missing required field
        sync_messages = [
            message
            for message in sync_messages
            if message.get("propertyNameToValues", {}).get("email")
        ]

    while len(sync_messages) > 0:
        staged_messages = sync_messages[0:200]
        sync_messages = sync_messages[200:]

        if print_to_console:
            print("    Sending sync message...")
        response = send_hubspot_request(
            object_type, HUBSPOT_SYNC_URL, "PUT", body=staged_messages
        )
        try:
            response.raise_for_status()
        except HTTPError:
            if print_to_console:
                print(
                    "    Sync message failed with status {} and message {}".format(
                        response.status_code, response.json().get("message")
                    )
                )
            else:
                log.exception("Bulk sync failed for %s", object_type)
