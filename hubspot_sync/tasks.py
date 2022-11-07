"""
Hubspot tasks
"""
import logging
import re

from main.celery import app

from hubspot_sync import api

log = logging.getLogger(__name__)

HUBSPOT_SYNC_URL = "/extensions/ecomm/v1/sync-messages"
ASSOCIATED_DEAL_RE = re.compile(r"\[hs_assoc__deal_id: (.+)\]")


@app.task
def sync_contact_with_hubspot(user_id):
    """Send a sync-message to sync a user with a hubspot_sync contact"""
    return api.sync_contact_with_hubspot(user_id).id


@app.task
def sync_product_with_hubspot(bootcamp_run_id):
    """Send a sync-message to sync a BootcampRun with a hubspot_sync product"""
    return api.sync_product_with_hubspot(bootcamp_run_id).id


@app.task
def sync_deal_with_hubspot(application_id):
    """ Sync the application to a hubspot_sync deal and line"""
    return api.sync_deal_with_hubspot(application_id).id
