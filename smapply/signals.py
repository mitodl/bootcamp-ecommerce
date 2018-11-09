"""Signals for fluidreview models"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from smapply.api import parse_webhook
from fluidreview.constants import WebhookParseStatus
from smapply.models import WebhookRequestSMA


@receiver(post_save, sender=WebhookRequestSMA, dispatch_uid="webhookrequest_sma_post_save")
def handle_parse_webhook(sender, instance, created, **kwargs):  # pylint:disable=unused-argument
    """
    Extract individual attribute values from a WebhookRequest body; create/update User & Profile if necessary
    """
    if created and instance.status == WebhookParseStatus.CREATED:
        parse_webhook(instance)
