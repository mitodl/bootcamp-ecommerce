"""
Admin views for jobma
"""

from django.contrib import admin

from jobma.models import Interview, Job


class InterviewAdmin(admin.ModelAdmin):
    """Admin for Interview"""

    model = Interview

    list_display = ("id", "get_applicant_email", "get_job_title", "status")
    raw_id_fields = ("job", "applicant")
    search_fields = ("applicant__email", "applicant__username")
    list_filter = ("status",)

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("applicant", "job")

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        # Move "status" column directly underneath "applicant" in detail view
        fields.remove("status")
        applicant_index = fields.index("applicant")
        fields.insert(applicant_index + 1, "status")
        return fields

    def get_applicant_email(self, obj):
        """Returns the user email"""
        return obj.applicant.email

    get_applicant_email.short_description = "Applicant"
    get_applicant_email.admin_order_field = "applicant__email"

    def get_job_title(self, obj):
        """Returns the job title"""
        return obj.job.job_title

    get_job_title.short_description = "Job Title"
    get_job_title.admin_order_field = "job__job_title"


class JobAdmin(admin.ModelAdmin):
    """Admin for Job"""

    model = Job

    list_display = ("id", "job_id", "job_title", "get_run_display_title")
    raw_id_fields = ("run",)
    search_fields = ("job_title", "job_code", "run__title", "run__bootcamp__title")
    list_filter = ("run__bootcamp__title",)

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("run__bootcamp")

    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        return obj.run.display_title

    get_run_display_title.short_description = "Bootcamp Run"
    get_run_display_title.admin_order_field = "run__title"


admin.site.register(Interview, InterviewAdmin)
admin.site.register(Job, JobAdmin)
