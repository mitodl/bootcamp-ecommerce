"""Signals for fluidreview models"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from fluidreview.api import FluidReviewAPI, process_user, parse_webhook
from fluidreview.constants import WebhookParseStatus
from fluidreview.models import WebhookRequest
from fluidreview.serializers import UserSerializer
from profiles.models import Profile


@receiver(post_save, sender=WebhookRequest, dispatch_uid="webhookrequest_post_save")
def handle_parse_webhook(sender, instance, created, **kwargs):  # pylint:disable=unused-argument
    """
    Extract individual attribute values from a WebhookRequest body; create/update User & Profile if necessary
    """
    if created and instance.status == WebhookParseStatus.CREATED:
        parse_webhook(instance)
        if instance.status == WebhookParseStatus.SUCCEEDED:
            if not Profile.objects.filter(fluidreview_id=instance.user_id):
                # Get user info from FluidReview API (ensures that webhook user_id is real).
                user_info = FluidReviewAPI().get('/users/{}'.format(instance.user_id)).json()
                serializer = UserSerializer(data=user_info)
                serializer.is_valid(raise_exception=True)
                process_user(serializer.data)
