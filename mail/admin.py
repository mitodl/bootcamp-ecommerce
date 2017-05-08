"""
Admin views for klasses
"""

from django.contrib import admin

from mail.models import (
    AutomaticReminderEmail,
    SentAutomaticEmails,
)


class AutomaticReminderEmailAdmin(admin.ModelAdmin):
    """Admin for AutomaticReminderEmail"""
    model = AutomaticReminderEmail
    list_display = ('reminder_type', 'days_before',)


class SentAutomaticEmailsAdmin(admin.ModelAdmin):
    """Admin for SentAutomaticEmails"""
    model = SentAutomaticEmails
    list_display = ('user', 'automatic_email',)


admin.site.register(AutomaticReminderEmail, AutomaticReminderEmailAdmin)
admin.site.register(SentAutomaticEmails, SentAutomaticEmailsAdmin)
