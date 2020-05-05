"""
Admin views for bootcamp applications
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from applications import models
from main.admin import TimestampedModelAdmin


class ApplicationStepAdmin(admin.ModelAdmin):
    """Admin for ApplicationStep"""
    model = models.ApplicationStep
    list_display = ('id', 'get_bootcamp_title', 'submission_type', 'step_order')
    ordering = ("bootcamp", "step_order")

    def get_bootcamp_title(self, obj):
        """Returns the bootcamp title"""
        return obj.bootcamp.title

    get_bootcamp_title.short_description = "Bootcamp"
    get_bootcamp_title.admin_order_field = "bootcamp__title"


class BootcampRunApplicationStepAdmin(admin.ModelAdmin):
    """Admin for BootcampRunApplicationStep"""
    model = models.BootcampRunApplicationStep
    list_display = ('id', 'get_bootcamp_title', 'get_run_title', 'due_date', 'get_submission_type', 'get_step_order')
    list_filter = ("bootcamp_run__bootcamp",)
    raw_id_fields = ("bootcamp_run",)
    ordering = ("bootcamp_run__bootcamp", "bootcamp_run", "application_step__step_order")

    def get_bootcamp_title(self, obj):
        """Returns the bootcamp title"""
        return obj.bootcamp_run.bootcamp.title

    get_bootcamp_title.short_description = "Bootcamp"
    get_bootcamp_title.admin_order_field = "bootcamp_run__bootcamp__title"

    def get_run_title(self, obj):
        """Returns the bootcamp run title"""
        return obj.bootcamp_run.title

    get_run_title.short_description = "Bootcamp Run"
    get_run_title.admin_order_field = "bootcamp_run__title"

    def get_submission_type(self, obj):
        """Returns the application step submission type"""
        return obj.application_step.submission_type

    get_submission_type.short_description = "Submission Type"
    get_submission_type.admin_order_field = "application_step__submission_type"

    def get_step_order(self, obj):
        """Returns the application step order"""
        return obj.application_step.step_order

    get_step_order.short_description = "Submission Type"
    get_step_order.admin_order_field = "application_step__step_order"


class BootcampApplicationAdmin(TimestampedModelAdmin):
    """Admin for BootcampApplication"""
    model = models.BootcampApplication
    list_display = ('id', 'get_user_email', 'get_bootcamp_title', 'get_run_title', 'state')
    search_fields = ("user__email", "user__username")
    list_filter = ("bootcamp_run__bootcamp",)
    raw_id_fields = ("user", "bootcamp_run", "order")

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super().get_queryset(request).select_related("user", "bootcamp_run__bootcamp")
        )

    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.user.email

    get_user_email.short_description = "User"
    get_user_email.admin_order_field = "user__email"

    def get_bootcamp_title(self, obj):
        """Returns the bootcamp title"""
        return obj.bootcamp_run.bootcamp.title

    get_bootcamp_title.short_description = "Bootcamp"
    get_bootcamp_title.admin_order_field = "bootcamp_run__bootcamp__title"

    def get_run_title(self, obj):
        """Returns the bootcamp run title"""
        return obj.bootcamp_run.title

    get_run_title.short_description = "Bootcamp Run"
    get_run_title.admin_order_field = "bootcamp_run__title"


class SubmissionTypeAdmin(TimestampedModelAdmin):
    """Base admin class for submission types"""
    list_display = ('id', 'get_user_email', 'get_run_title', 'app_step_submission_link')
    readonly_fields = ('get_user_email', 'get_run_title', 'app_step_submission_link')
    search_fields = (
        "app_step_submissions__bootcamp_application__user__email",
        "app_step_submissions__bootcamp_application__bootcamp_run__title",
        "app_step_submissions__bootcamp_application__bootcamp_run__bootcamp__title",
    )

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super().get_queryset(request).prefetch_related(
                "app_step_submissions__bootcamp_application__user",
                "app_step_submissions__bootcamp_application__bootcamp_run",
            )
        )

    def get_user_email(self, obj):
        """Returns the user email"""
        app_step_submission = obj.app_step_submissions.first()
        return app_step_submission.bootcamp_application.user.email

    get_user_email.short_description = "Application User"
    get_user_email.admin_order_field = "app_step_submission__bootcamp_application__user__email"

    def get_run_title(self, obj):
        """Returns the bootcamp run title"""
        app_step_submission = obj.app_step_submissions.first()
        return app_step_submission.bootcamp_application.bootcamp_run.title

    get_run_title.short_description = "Application Bootcamp Run"
    get_run_title.admin_order_field = "app_step_submission__bootcamp_application__bootcamp_run__title"

    def app_step_submission_link(self, obj):
        """Returns a link to the related bootcamp application"""
        app_step_submission = obj.app_step_submissions.first()
        return mark_safe('<a href="{}">Submission ({})</a>'.format(
            reverse(
                "admin:applications_{}_change".format(models.ApplicationStepSubmission._meta.model_name),
                args=(app_step_submission.id,)
            ),  # pylint: disable=protected-access
            app_step_submission.id
        ))
    app_step_submission_link.short_description = 'Application Submission'


class VideoInterviewSubmissionAdmin(SubmissionTypeAdmin):
    """Admin class for VideoInterviewSubmission"""
    model = models.VideoInterviewSubmission

    def get_list_display(self, request):
        return tuple(super().get_list_display(request) or ()) + ("video_file",)


class QuizSubmissionAdmin(SubmissionTypeAdmin):
    """Admin for QuizSubmission"""
    model = models.QuizSubmission

    def get_list_display(self, request):
        return tuple(super().get_list_display(request) or ()) + ("started_date",)


class ApplicationStepSubmissionAdmin(TimestampedModelAdmin):
    """Admin for ApplicationStepSubmission"""
    model = models.ApplicationStepSubmission
    list_display = (
        'id',
        'bootcamp_application_id',
        'get_user_email',
        'get_run_title',
        'content_type',
        'submission_content_obj_link',
    )
    list_filter = ("bootcamp_application__bootcamp_run",)
    raw_id_fields = ("bootcamp_application", "run_application_step",)
    readonly_fields = ("submission_content_obj_link",)

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super().get_queryset(request)
            .select_related("bootcamp_application__user", "bootcamp_application__bootcamp_run")
            .prefetch_related("content_object")
        )

    def get_readonly_fields(self, request, obj=None):
        # Only allow the content_type and object_id to be set if a new object is being created. Otherwise, set those
        # to readonly.
        if obj and obj.id is not None:
            return tuple(self.readonly_fields or ()) + ("content_type", "object_id")
        return self.readonly_fields

    def submission_content_obj_link(self, obj):
        """Returns a link to the content object"""
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse(
                "admin:applications_{}_change".format(obj.content_object._meta.model_name),
                args=(obj.object_id,)
            ),  # pylint: disable=protected-access
            obj.content_object
        ))
    submission_content_obj_link.short_description = 'submission object'

    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.bootcamp_application.user.email

    get_user_email.short_description = "User"
    get_user_email.admin_order_field = "user__email"

    def get_run_title(self, obj):
        """Returns the bootcamp run title"""
        return obj.bootcamp_application.bootcamp_run.title

    get_run_title.short_description = "Bootcamp Run"
    get_run_title.admin_order_field = "bootcamp_run__title"


admin.site.register(models.ApplicationStep, ApplicationStepAdmin)
admin.site.register(models.BootcampRunApplicationStep, BootcampRunApplicationStepAdmin)
admin.site.register(models.BootcampApplication, BootcampApplicationAdmin)
admin.site.register(models.VideoInterviewSubmission, VideoInterviewSubmissionAdmin)
admin.site.register(models.QuizSubmission, QuizSubmissionAdmin)
admin.site.register(models.ApplicationStepSubmission, ApplicationStepSubmissionAdmin)
