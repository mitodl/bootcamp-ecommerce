"""
Admin views for bootcamp applications
"""

from django import forms
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from mitol.common.admin import TimestampedModelAdmin

from applications.models import (
    ApplicationStep,
    ApplicationStepSubmission,
    BootcampRunApplicationStep,
    BootcampApplication,
    VideoInterviewSubmission,
    QuizSubmission,
    ApplicantLetter,
    Interview,
)
from ecommerce.models import Order
from main.utils import get_field_names


@admin.register(ApplicationStep)
class ApplicationStepAdmin(admin.ModelAdmin):
    """Admin for ApplicationStep"""

    model = ApplicationStep
    list_display = ("id", "get_bootcamp_title", "submission_type", "step_order")
    ordering = ("bootcamp", "step_order")

    @admin.display(
        description="Bootcamp",
        ordering="bootcamp__title",
    )
    def get_bootcamp_title(self, obj):
        """Returns the bootcamp title"""
        return obj.bootcamp.title


@admin.register(BootcampRunApplicationStep)
class BootcampRunApplicationStepAdmin(admin.ModelAdmin):
    """Admin for BootcampRunApplicationStep"""

    model = BootcampRunApplicationStep
    list_display = (
        "id",
        "get_run_display_title",
        "get_submission_type",
        "get_step_order",
        "due_date",
    )
    list_filter = ("bootcamp_run__bootcamp",)
    raw_id_fields = ("bootcamp_run", "application_step")
    ordering = (
        "bootcamp_run__bootcamp",
        "bootcamp_run",
        "application_step__step_order",
    )

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("bootcamp_run__bootcamp")

    @admin.display(
        description="Bootcamp Run",
        ordering="bootcamp_run__title",
    )
    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        return obj.bootcamp_run.display_title

    @admin.display(
        description="Submission Type",
        ordering="application_step__submission_type",
    )
    def get_submission_type(self, obj):
        """Returns the application step submission type"""
        return obj.application_step.submission_type

    @admin.display(
        description="Step Order",
        ordering="application_step__step_order",
    )
    def get_step_order(self, obj):
        """Returns the application step order"""
        return obj.application_step.step_order


class OrderInline(admin.StackedInline):
    """Inline form for Order"""

    model = Order
    readonly_fields = get_field_names(Order)
    extra = 0
    show_change_link = True
    can_delete = False
    ordering = ("-created_on",)
    min_num = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(BootcampApplication)
class BootcampApplicationAdmin(TimestampedModelAdmin):
    """Admin for BootcampApplication"""

    model = BootcampApplication
    include_timestamps_in_list = True
    inlines = [OrderInline]
    list_display = ("id", "get_user_email", "get_run_display_title", "state")
    search_fields = (
        "user__email",
        "user__username",
        "bootcamp_run__title",
        "bootcamp_run__bootcamp__title",
    )
    list_filter = ("bootcamp_run__bootcamp", "state")
    raw_id_fields = ("user", "bootcamp_run")

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super()
            .get_queryset(request)
            .select_related("user", "bootcamp_run__bootcamp")
        )

    @admin.display(
        description="User",
        ordering="user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.user.email

    @admin.display(
        description="Bootcamp Run",
        ordering="bootcamp_run__title",
    )
    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        return obj.bootcamp_run.display_title


class AppStepSubmissionInline(GenericTabularInline):
    """Admin class for ApplicationStepSubmission"""

    model = ApplicationStepSubmission
    max_num = 1
    raw_id_fields = ("bootcamp_application", "run_application_step")


class SubmissionTypeAdmin(TimestampedModelAdmin):
    """Base admin class for submission types"""

    list_display = (
        "id",
        "get_user_email",
        "get_run_display_title",
        "app_step_submission_link",
    )
    readonly_fields = (
        "get_user_email",
        "get_run_display_title",
        "app_step_submission_link",
    )
    search_fields = (
        "app_step_submissions__bootcamp_application__user__email",
        "app_step_submissions__bootcamp_application__bootcamp_run__title",
        "app_step_submissions__bootcamp_application__bootcamp_run__bootcamp__title",
    )
    inlines = [AppStepSubmissionInline]
    include_created_on_in_list = True

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                "app_step_submissions__bootcamp_application__user",
                "app_step_submissions__bootcamp_application__bootcamp_run__bootcamp",
            )
        )

    @admin.display(
        description="Application User",
        ordering="app_step_submission__bootcamp_application__user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        app_step_submissions = obj.app_step_submissions.all()
        return (
            None
            if len(app_step_submissions) == 0
            else app_step_submissions[0].bootcamp_application.user.email
        )

    @admin.display(
        description="App Bootcamp Run",
        ordering="app_step_submission__bootcamp_application__bootcamp_run__title",
    )
    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        app_step_submissions = obj.app_step_submissions.all()
        return (
            None
            if len(app_step_submissions) == 0
            else app_step_submissions[0].bootcamp_application.bootcamp_run.display_title
        )

    @admin.display(description="Submission")
    def app_step_submission_link(self, obj):
        """Returns a link to the related bootcamp application"""
        app_step_submissions = obj.app_step_submissions.all()
        if len(app_step_submissions) == 0:
            return None
        app_step_submission = app_step_submissions[0]
        return mark_safe(
            '<a href="{}">Submission ({})</a>'.format(
                reverse(
                    "admin:applications_{}_change".format(
                        ApplicationStepSubmission._meta.model_name
                    ),
                    args=(app_step_submission.id,),
                ),  # pylint: disable=protected-access
                app_step_submission.id,
            )
        )


@admin.register(VideoInterviewSubmission)
class VideoInterviewSubmissionAdmin(SubmissionTypeAdmin):
    """Admin class for VideoInterviewSubmission"""

    model = VideoInterviewSubmission

    raw_id_fields = ("interview",)

    def get_list_display(self, request):
        return tuple(super().get_list_display(request) or ()) + ("interview_link",)

    @admin.display(description="Interview")
    def interview_link(self, obj):
        """Returns a link to the related interview record"""
        if not hasattr(obj, "interview") or obj.interview is None:
            return None
        return mark_safe(
            '<a href="{}">Interview ({})</a>'.format(
                reverse(
                    "admin:jobma_{}_change".format(Interview._meta.model_name),
                    args=(obj.interview.id,),
                ),  # pylint: disable=protected-access
                obj.interview.id,
            )
        )


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(SubmissionTypeAdmin):
    """Admin for QuizSubmission"""

    model = QuizSubmission

    def get_list_display(self, request):
        return tuple(super().get_list_display(request) or ()) + ("started_date",)


class ApplicationStepSubmissionForm(forms.ModelForm):
    """Form for ApplicationStepSubmission admin"""

    def clean_object_id(self):
        """Validates the object_id input"""
        content_type = self.cleaned_data.get("content_type")
        object_id = self.cleaned_data.get("object_id")
        if (
            content_type
            and not content_type.model_class().objects.filter(id=object_id).exists()
        ):
            raise ValidationError(
                f"The object_id must match the id of a {content_type.model} object"
            )
        return object_id


@admin.register(ApplicationStepSubmission)
class ApplicationStepSubmissionAdmin(TimestampedModelAdmin):
    """Admin for ApplicationStepSubmission"""

    model = ApplicationStepSubmission
    form = ApplicationStepSubmissionForm
    list_display = (
        "id",
        "get_user_email",
        "get_run_display_title",
        "review_status",
        "content_type",
        "submission_content_obj_link",
    )
    list_filter = ("review_status", "bootcamp_application__bootcamp_run__bootcamp")
    raw_id_fields = ("bootcamp_application", "run_application_step")
    readonly_fields = ("submission_content_obj_link",)
    search_fields = (
        "bootcamp_application__user__email",
        "bootcamp_application__bootcamp_run__title",
        "bootcamp_application__bootcamp_run__bootcamp__title",
    )

    def get_queryset(self, request):
        """Overrides base queryset"""
        return (
            super()
            .get_queryset(request)
            .select_related(
                "bootcamp_application__user",
                "bootcamp_application__bootcamp_run__bootcamp",
            )
            .prefetch_related("content_object")
        )

    def get_readonly_fields(self, request, obj=None):
        # Only allow the content_type and object_id to be set if a new object is being created. Otherwise, set those
        # to readonly.
        if obj and obj.id is not None:
            return tuple(self.readonly_fields or ()) + ("content_type", "object_id")
        return self.readonly_fields

    @admin.display(description="submission object")
    def submission_content_obj_link(self, obj):
        """Returns a link to the content object"""
        if obj.content_object is None:
            return None
        return mark_safe(
            '<a href="{}">{}</a>'.format(
                reverse(
                    "admin:applications_{}_change".format(
                        obj.content_object._meta.model_name
                    ),
                    args=(obj.object_id,),
                ),  # pylint: disable=protected-access
                obj.content_object,
            )
        )

    @admin.display(
        description="User",
        ordering="user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.bootcamp_application.user.email

    @admin.display(
        description="Bootcamp Run",
        ordering="bootcamp_run__title",
    )
    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        return obj.bootcamp_application.bootcamp_run.display_title


@admin.register(ApplicantLetter)
class ApplicantLetterAdmin(TimestampedModelAdmin):
    """Admin for ApplicantLetter"""

    model = ApplicantLetter
    list_display = ("id", "letter_type", "get_user_email", "get_run_display_title")
    list_filter = ("letter_type",)
    raw_id_fields = ("application",)
    search_fields = (
        "application__user__email",
        "application__bootcamp_run__title",
        "application__bootcamp_run__bootcamp__title",
    )
    readonly_fields = get_field_names(ApplicantLetter)

    @admin.display(
        description="User",
        ordering="user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.application.user.email

    @admin.display(
        description="Bootcamp Run",
        ordering="bootcamp_run__title",
    )
    def get_run_display_title(self, obj):
        """Returns the bootcamp run display title"""
        return obj.application.bootcamp_run.display_title
