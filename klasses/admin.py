"""
Admin views for bootcamps
"""

from django.contrib import admin
from mitol.common.admin import TimestampedModelAdmin

from klasses.models import (
    Bootcamp,
    BootcampRun,
    BootcampRunCertificate,
    BootcampRunEnrollment,
    Installment,
    PersonalPrice,
)


class BootcampRunInline(admin.StackedInline):
    """Admin Inline for BootcampRun objects"""

    model = BootcampRun
    extra = 1
    show_change_link = True


class InstallmentInline(admin.StackedInline):
    """Admin Inline for Installment objects"""

    model = Installment
    extra = 1
    show_change_link = True


@admin.register(Bootcamp)
class BootcampAdmin(admin.ModelAdmin):
    """Admin for Bootcamp"""

    model = Bootcamp
    list_display = (
        "title",
        "readable_id",
    )
    search_fields = (
        "title",
        "readable_id",
    )
    inlines = [BootcampRunInline]


@admin.register(BootcampRun)
class BootcampRunAdmin(admin.ModelAdmin):
    """Admin for BootcampRun"""

    model = BootcampRun
    list_display = (
        "display_title",
        "bootcamp_run_id",
        "novoed_course_stub",
        "start_date",
        "end_date",
    )
    raw_id_fields = ("bootcamp",)
    search_fields = (
        "title",
        "novoed_course_stub",
        "bootcamp_run_id",
        "bootcamp__title",
    )
    inlines = [InstallmentInline]


@admin.register(BootcampRunEnrollment)
class BootcampRunEnrollmentAdmin(TimestampedModelAdmin):
    """Admin for BootcampRunEnrollment"""

    model = BootcampRunEnrollment
    include_created_on_in_list = True
    list_display = (
        "id",
        "get_user_email",
        "bootcamp_run",
        "change_status",
        "active",
        "user_certificate_is_blocked",
    )
    list_filter = (
        "change_status",
        "active",
        "bootcamp_run__bootcamp",
        "bootcamp_run",
        "user_certificate_is_blocked",
    )
    raw_id_fields = ("bootcamp_run", "user")
    search_fields = (
        "user__email",
        "user__username",
        "bootcamp_run__title",
        "bootcamp_run__bootcamp__title",
    )

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


@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""

    model = Installment
    list_display = ("id", "bootcamp_run", "deadline", "amount")
    raw_id_fields = ("bootcamp_run",)
    search_fields = (
        "bootcamp_run__title",
        "bootcamp_run__bootcamp__title",
    )


@admin.register(PersonalPrice)
class PersonalPriceAdmin(admin.ModelAdmin):
    """Admin for PersonalPrice"""

    model = PersonalPrice
    list_display = ("id", "get_user_email", "bootcamp_run", "price")
    list_filter = ("bootcamp_run__bootcamp",)
    raw_id_fields = ("bootcamp_run", "user")
    search_fields = (
        "price",
        "bootcamp_run__title",
        "user__email",
        "user__username",
        "user__profile__name",
        "user__legal_address__first_name",
        "user__legal_address__last_name",
    )

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


@admin.register(BootcampRunCertificate)
class BootcampRunCertificateAdmin(TimestampedModelAdmin):
    """Admin for BootcampRunCertificate"""

    model = BootcampRunCertificate
    include_timestamps_in_list = True
    list_display = ["uuid", "get_user_email", "bootcamp_run", "get_revoked_state"]
    search_fields = [
        "bootcamp_run__id",
        "bootcamp_run__title",
        "user__username",
        "user__email",
    ]
    raw_id_fields = ("user",)

    def get_queryset(self, request):  # noqa: ARG002, D102
        return self.model.all_objects.get_queryset().select_related(
            "user", "bootcamp_run"
        )

    @admin.display(
        description="Active",
        boolean=True,
    )
    def get_revoked_state(self, obj):
        """Return the revoked state"""
        return obj.is_revoked is not True

    @admin.display(
        description="User",
        ordering="user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.user.email
