"""Tasks for smapply"""
from bootcamp.celery import app
from hubspot.task_helpers import sync_hubspot_user
from smapply.serializers import UserSerializer
from smapply.api import list_users, process_user
from profiles.models import Profile


@app.task
def sync_all_users():
    """
    Pulls user data from SMApply and creates or conditionally updates local User and Profile objects
    """
    for sma_user in list_users():
        profile = Profile.objects.filter(smapply_id=sma_user['id']).first()
        if not profile:
            serializer = UserSerializer(data=sma_user)
            if serializer.is_valid():
                user = process_user(serializer.data)
                user.profile.smapply_user_data = sma_user
                user.profile.save()

                sync_hubspot_user(user.profile)
