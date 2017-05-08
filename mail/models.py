"""
Models for the mail app
"""
from django.contrib.auth.models import User
from django.db import models

from klasses.models import Klass


class AutomaticReminderEmail(models.Model):
    """
    Stores information for an automatically sent email
    """
    PAYMENT_APPROACHING = 'payment_approaching'
    REMINDER_TYPES = [PAYMENT_APPROACHING]
    reminder_type = models.CharField(
        choices=[(reminder_type, reminder_type) for reminder_type in REMINDER_TYPES],
        default=PAYMENT_APPROACHING,
        max_length=30,
    )
    days_before = models.SmallIntegerField(null=False, blank=False)
    email_subject = models.TextField(null=False, blank=True)
    email_body = models.TextField(null=False, blank=True)
    sender_name = models.TextField(null=False, blank=True)

    def __str__(self):
        """String representation of AutomaticEmail"""
        return "AutomaticEmail reminder_type={}, days_before={}".format(self.reminder_type, self.days_before)


class SentAutomaticEmails(models.Model):
    """
    Stores informations about emails sent to users
    """
    user = models.ForeignKey(User, null=False)
    automatic_email = models.ForeignKey(AutomaticReminderEmail, null=False)
    klass = models.ForeignKey(Klass, null=False)

    def __str__(self):
        """String representation of SentAutomaticEmails"""
        return "SentAutomaticEmails for user={}, klass={}, email={}".format(
            self.user, self.klass, self.automatic_email)
