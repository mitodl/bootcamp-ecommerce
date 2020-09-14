"""
Admin views for bootcamps
"""
from django.contrib import admin

from klasses import models
from main.admin import TimestampedModelAdmin


class BootcampRunInline(admin.StackedInline):
    """Admin Inline for BootcampRun objects"""

    model = models.BootcampRun
    extra = 1
    show_change_link = True


class InstallmentInline(admin.StackedInline):
    """Admin Inline for Installment objects"""

    model = models.Installment
    extra = 1
    show_change_link = True


class BootcampAdmin(admin.ModelAdmin):
    """Admin for Bootcamp"""

    model = models.Bootcamp
    list_display = ("title",)
    inlines = [BootcampRunInline]


class BootcampRunAdmin(admin.ModelAdmin):
    """Admin for BootcampRun"""

    model = models.BootcampRun
    list_display = ("display_title", "novoed_course_stub", "start_date", "end_date")
    raw_id_fields = ("bootcamp",)
    inlines = [InstallmentInline]


class BootcampRunEnrollmentAdmin(TimestampedModelAdmin):
    """Admin for BootcampRunEnrollment"""

    model = models.BootcampRunEnrollment
    include_created_on_in_list = True
    list_display = ("id", "bootcamp_run", "user", "change_status", "active")
    list_filter = ("change_status", "active", "bootcamp_run__bootcamp")
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


class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""

    model = models.Installment
    list_display = ("id", "bootcamp_run", "deadline", "amount")
    raw_id_fields = ("bootcamp_run",)


class PersonalPriceAdmin(admin.ModelAdmin):
    """Admin for PersonalPrice"""

    model = models.PersonalPrice
    list_display = ("id", "bootcamp_run", "user", "price")
    list_filter = ("bootcamp_run__bootcamp", "bootcamp_run")
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


admin.site.register(models.Bootcamp, BootcampAdmin)
admin.site.register(models.BootcampRun, BootcampRunAdmin)
admin.site.register(models.Installment, InstallmentAdmin)
admin.site.register(models.PersonalPrice, PersonalPriceAdmin)
admin.site.register(models.BootcampRunEnrollment, BootcampRunEnrollmentAdmin)
