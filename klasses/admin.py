"""
Admin views for klasses
"""

from django.contrib import admin

from klasses.models import (
    Bootcamp,
    Installment,
    Klass,
)


class BootcampAdmin(admin.ModelAdmin):
    """Admin for Bootcamp"""
    model = Bootcamp


class KlassAdmin(admin.ModelAdmin):
    """Admin for Klass"""
    model = Klass


class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""
    model = Installment


admin.site.register(Bootcamp, BootcampAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Installment, InstallmentAdmin)
