"""
Admin views for jobma
"""

from django.contrib import admin

from jobma.models import Interview, Job


class InterviewAdmin(admin.ModelAdmin):
    """Admin for Interview"""
    model = Interview


class JobAdmin(admin.ModelAdmin):
    """Admin for Job"""
    model = Job


admin.site.register(Interview, InterviewAdmin)
admin.site.register(Job, JobAdmin)
