""" Hubspot models """
from django.db import models

from applications.models import BootcampApplication


class HubspotErrorCheck(models.Model):
    """
    Store the datetime of the most recent Hubspot API error check.
    """

    checked_on = models.DateTimeField()


class HubspotLineResync(models.Model):
    """
    Indicates that hubspot tried to sync a line before it's deal and needs to be resynced
    """

    application = models.ForeignKey(
        BootcampApplication, null=True, on_delete=models.CASCADE
    )
