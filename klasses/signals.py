"""Signals for ecommerce models"""

from django.db.models.signals import post_delete, post_save
from django.db.transaction import on_commit
from django.dispatch import receiver

from hubspot_sync.task_helpers import sync_hubspot_product
from klasses.api import adjust_app_state_for_new_price
from klasses.models import BootcampRun, PersonalPrice


@receiver(post_save, sender=BootcampRun, dispatch_uid="bootcamp__run_post_save")
def sync_bootcamp_run(sender, instance, created, **kwargs):  # noqa: ARG001
    """Sync bootcamp run to hubspot"""
    on_commit(lambda: sync_hubspot_product(instance))


@receiver(post_save, sender=PersonalPrice, dispatch_uid="personal_price_post_save")
def personal_price_post_save(sender, instance, created, **kwargs):  # noqa: ARG001
    """Handles the 'post_save' signal from the PersonalPrice model"""
    on_commit(
        lambda: adjust_app_state_for_new_price(
            user=instance.user,
            bootcamp_run=instance.bootcamp_run,
            new_price=instance.price,
        )
    )


@receiver(post_delete, sender=PersonalPrice, dispatch_uid="personal_price_post_delete")
def personal_price_post_delete(sender, instance, **kwargs):  # noqa: ARG001
    """Handles the 'post_save' signal from the PersonalPrice model"""
    on_commit(
        lambda: adjust_app_state_for_new_price(
            user=instance.user, bootcamp_run=instance.bootcamp_run
        )
    )
