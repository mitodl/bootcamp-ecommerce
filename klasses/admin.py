"""
Admin views for bootcamps
"""
from django.contrib import admin

from klasses import models


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
    list_display = ("display_title",)
    inlines = [InstallmentInline]


class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""

    model = models.Installment
    list_display = ("bootcamp_run", "deadline", "amount")


class PersonalPriceAdmin(admin.ModelAdmin):
    """Admin for PersonalPrice"""

    model = models.PersonalPrice
    list_display = ("bootcamp_run", "user", "price")


admin.site.register(models.Bootcamp, BootcampAdmin)
admin.site.register(models.BootcampRun, BootcampRunAdmin)
admin.site.register(models.Installment, InstallmentAdmin)
admin.site.register(models.PersonalPrice, PersonalPriceAdmin)
