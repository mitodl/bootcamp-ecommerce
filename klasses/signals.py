"""Signals for ecommerce models"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from hubspot.task_helpers import sync_hubspot_product
from klasses.models import Bootcamp


@receiver(post_save, sender=Bootcamp, dispatch_uid="bootcamp_post_save")
def sync_bootcamp(
    sender, instance, created, **kwargs
):  # pylint:disable=unused-argument

    """Sync bootcamp to hubspot"""
    sync_hubspot_product(instance)
