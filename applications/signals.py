"""Signals for application models"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import BootcampApplication, ApplicationStepSubmission
from hubspot.task_helpers import sync_hubspot_application

# pylint:disable=unused-argument


@receiver(
    post_save, sender=BootcampApplication, dispatch_uid="bootcamp_application_post_save"
)
def sync_deal_application(sender, instance, created, **kwargs):
    """Sync application to hubspot"""
    if not created:
        sync_hubspot_application(instance)


@receiver(
    post_save,
    sender=ApplicationStepSubmission,
    dispatch_uid="application_step_submission_post_save",
)
def sync_deal_on_submission(sender, instance, created, **kwargs):
    """Sync application to hubspot when a submission is created"""
    if created:
        sync_hubspot_application(instance.bootcamp_application)
