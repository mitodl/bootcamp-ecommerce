"""
Admin site bindings for profiles
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as ContribUserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from hijack.contrib.admin import HijackUserAdminMixin

from profiles.models import LegalAddress, Profile

User = get_user_model()


class UserLegalAddressInline(admin.StackedInline):
    """Admin view for the legal address"""

    model = LegalAddress
    classes = ["collapse"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    ("first_name", "last_name"),
                    "street_address_1",
                    "street_address_2",
                    "street_address_3",
                    "street_address_4",
                    "street_address_5",
                    ("city", "state_or_territory", "postal_code"),
                    "country",
                )
            },
        ),
    )

    def has_delete_permission(self, request, obj=None):
        return False


class UserProfileInline(admin.StackedInline):
    """Admin view for the profile"""

    model = Profile
    classes = ["collapse"]

    def has_delete_permission(self, request, obj=None):
        return True


class UserAdmin(ContribUserAdmin, HijackUserAdminMixin):
    """Admin views for user"""

    fieldsets = (
        (None, {"fields": ("username", "password", "last_login")}),
        (_("Personal Info"), {"fields": ("email",)}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["collapse"],
            },
        ),
    )
    list_display = ("username", "email", "is_staff", "last_login")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("username", "email")
    ordering = ("email",)
    readonly_fields = ("username", "last_login")
    inlines = [UserLegalAddressInline, UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
