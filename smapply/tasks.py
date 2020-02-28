"""Tasks for smapply"""
import logging
from bootcamp.celery import app
from hubspot.api import make_contact_sync_message
from hubspot.tasks import sync_bulk_with_hubspot
from smapply.api import list_users, process_user, SMApplyTaskCache
from profiles.models import Profile

log = logging.getLogger(__name__)


@app.task
def sync_all_users():
    """
    Pulls user data from SMApply and creates or conditionally updates local User and Profile objects
    """
    profiles_to_sync = []
    for sma_user in list_users():
        # Only create Profile and User data for SMApply accounts with verified email addresses
        if not sma_user.get('email_verified'):
            continue

        profile = Profile.objects.filter(smapply_id=sma_user['id']).first()
        if not profile:
            try:
                user = process_user(sma_user)
                profiles_to_sync.append(user.profile)
            except:  # pylint: disable=bare-except
                log.exception('Syncing profile for SMA user %s failed', sma_user['id'])

    if profiles_to_sync:
        task_cache = SMApplyTaskCache()
        sync_bulk_with_hubspot(profiles_to_sync, make_contact_sync_message, "CONTACT", task_cache=task_cache)
