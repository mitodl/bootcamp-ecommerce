"""Tasks for smapply"""
from bootcamp.celery import app
from hubspot.api import make_contact_sync_message
from hubspot.tasks import sync_bulk_with_hubspot
from smapply.serializers import UserSerializer
from smapply.api import list_users, process_user, SMApplyTaskCache
from profiles.models import Profile


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
            serializer = UserSerializer(data=sma_user)
            if serializer.is_valid():
                user = process_user(sma_user)

                profiles_to_sync.append(user.profile)

    if profiles_to_sync:
        task_cache = SMApplyTaskCache()
        sync_bulk_with_hubspot(profiles_to_sync, make_contact_sync_message, "CONTACT", task_cache=task_cache)
