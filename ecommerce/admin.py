"""
Admin views for ecommerce models
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from main.admin import TimestampedModelAdmin
from main.utils import get_field_names
from ecommerce.models import Line, Order, OrderAudit, Receipt
from applications import models as application_models


class LineAdmin(TimestampedModelAdmin):
    """Admin for Line"""

    model = Line
    include_timestamps_in_list = True
    readonly_fields = get_field_names(Line)
    list_display = ("order", "run_key", "price", "description")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(TimestampedModelAdmin):
    """Admin for Order"""

    model = Order
    include_timestamps_in_list = True
    # Include all fields except "application" and "user", which will be replaced by more helpful equivalents
    fields = [
        name for name in get_field_names(Order) if name not in {"application", "user"}
    ] + ["get_user_email", "run_title", "application_link"]
    # Set all fields to readonly except "status"
    readonly_fields = [name for name in get_field_names(Order) if name != "status"] + [
        "get_user_email",
        "run_title",
        "application_link",
    ]
    list_display = ("id", "get_user_email", "status", "application_id")
    list_filter = ("status",)
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user", "application")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        """
        Saves object and logs change to object
        """
        obj.save_and_log(request.user)

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("user")

    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.user.email

    get_user_email.short_description = "User"
    get_user_email.admin_order_field = "user__email"

    def application_link(self, obj):
        """Returns a link to the related application"""
        if not hasattr(obj, "application") or obj.application is None:
            return None
        return mark_safe(
            '<a href="{}">Application ({})</a>'.format(
                reverse(
                    "admin:applications_{}_change".format(
                        application_models.BootcampApplication._meta.model_name
                    ),
                    args=(obj.application.id,),
                ),  # pylint: disable=protected-access
                obj.application.id,
            )
        )

    application_link.short_description = "Application"


class OrderAuditAdmin(admin.ModelAdmin):
    """Admin for OrderAudit"""

    model = OrderAudit
    readonly_fields = get_field_names(OrderAudit)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReceiptAdmin(TimestampedModelAdmin):
    """Admin for Receipt"""

    model = Receipt
    include_created_on_in_list = True
    readonly_fields = get_field_names(Receipt) + ["order_link"]
    list_display = ("id", "get_user_email", "order_link", "get_order_status")
    search_fields = ("order__user__email", "order__user__username")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("order__user")

    def get_user_email(self, obj):
        """Returns the user email"""
        if obj.order is None:
            return None
        return obj.order.user.email

    get_user_email.short_description = "User"
    get_user_email.admin_order_field = "order__user__email"

    def get_order_status(self, obj):
        """Returns the order status"""
        if obj.order is None:
            return None
        return obj.order.status

    get_order_status.short_description = "Status"
    get_order_status.admin_order_field = "order__status"

    def order_link(self, obj):
        """Returns a link to the related order"""
        if obj.order is None:
            return None
        return mark_safe(
            '<a href="{}">Order ({})</a>'.format(
                reverse(
                    "admin:ecommerce_{}_change".format(Order._meta.model_name),
                    args=(obj.order.id,),
                ),  # pylint: disable=protected-access
                obj.order.id,
            )
        )

    order_link.short_description = "Order"


admin.site.register(Line, LineAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderAudit, OrderAuditAdmin)
admin.site.register(Receipt, ReceiptAdmin)
