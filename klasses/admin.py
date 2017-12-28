"""
Admin views for klasses
"""

from django.contrib import admin

from klasses.models import (
    Bootcamp,
    Installment,
    Klass,
    PersonalPrice)


class KlassInline(admin.StackedInline):
    """Admin Inline for Klass objects"""
    model = Klass
    extra = 1
    show_change_link = True


class InstallmentInline(admin.StackedInline):
    """Admin Inline for Installment objects"""
    model = Installment
    extra = 1
    show_change_link = True


class BootcampAdmin(admin.ModelAdmin):
    """Admin for Bootcamp"""
    model = Bootcamp
    list_display = ('title', )
    inlines = [KlassInline]


class KlassAdmin(admin.ModelAdmin):
    """Admin for Klass"""
    model = Klass
    list_display = ('display_title', )
    inlines = [InstallmentInline]


class InstallmentAdmin(admin.ModelAdmin):
    """Admin for Installment"""
    model = Installment
    list_display = ('klass', 'deadline', 'amount')


class PersonalPriceAdmin(admin.ModelAdmin):
    """Admin for PersonalPrice"""
    model = PersonalPrice
    list_display = ('klass', 'user', 'price')


admin.site.register(Bootcamp, BootcampAdmin)
admin.site.register(Klass, KlassAdmin)
admin.site.register(Installment, InstallmentAdmin)
admin.site.register(PersonalPrice, PersonalPriceAdmin)
