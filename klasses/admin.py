"""
Admin views for klasses
"""

from django.contrib import admin

from klasses import models


class KlassInline(admin.StackedInline):
    """Admin Inline for Klass objects"""
    model = models.Klass
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
    list_display = ('title', )
    inlines = [KlassInline]


class KlassAdmin(admin.ModelAdmin):
    """Admin for Klass"""
    model = models.Klass
    list_display = ('display_title', )
    inlines = [InstallmentInline]


class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""
    model = models.Installment
    list_display = ('klass', 'deadline', 'amount')


class PersonalPriceAdmin(admin.ModelAdmin):
    """Admin for PersonalPrice"""
    model = models.PersonalPrice
    list_display = ('klass', 'user', 'price')


admin.site.register(models.Bootcamp, BootcampAdmin)
admin.site.register(models.Klass, KlassAdmin)
admin.site.register(models.Installment, InstallmentAdmin)
admin.site.register(models.PersonalPrice, PersonalPriceAdmin)
