"""Signals for application models"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import BootcampApplication
from hubspot.task_helpers import sync_hubspot_deal

log = logging.getLogger()


@receiver(post_save, sender=BootcampApplication, dispatch_uid="bootcamp_application_post_save")
def sync_deal_application(sender, instance, created, **kwargs):  # pylint:disable=unused-argument
    """Sync application to hubspot"""
    sync_hubspot_deal(instance)
