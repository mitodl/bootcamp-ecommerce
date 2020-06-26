"""Signals for ecommerce models"""
from django.db.transaction import on_commit
from django.db.models.signals import post_save
from django.dispatch import receiver

from hubspot.task_helpers import sync_hubspot_product
from klasses.models import BootcampRun


@receiver(post_save, sender=BootcampRun, dispatch_uid="bootcamp__run_post_save")
def sync_bootcamp_run(
    sender, instance, created, **kwargs
):  # pylint:disable=unused-argument

    """Sync bootcamp run to hubspot"""
    on_commit(lambda: sync_hubspot_product(instance))
