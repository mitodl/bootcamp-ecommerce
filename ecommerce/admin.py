"""
Admin views for ecommerce models
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from mitol.common.admin import TimestampedModelAdmin

from applications import models as application_models
from ecommerce.models import Line, Order, OrderAudit, Receipt, WireTransferReceipt
from main.utils import get_field_names


@admin.register(Line)
class LineAdmin(TimestampedModelAdmin):
    """Admin for Line"""

    search_fields = ["order__id", "order__user__email", "order__user__username"]
    model = Line
    include_timestamps_in_list = True
    readonly_fields = get_field_names(Line)
    list_display = ("order", "bootcamp_run_id", "price", "description")

    def has_add_permission(self, request):  # noqa: ARG002, D102
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False


class LineInline(admin.StackedInline):
    """Admin Inline for Line objects"""

    model = Line
    extra = 0
    show_change_link = True
    can_delete = False
    readonly_fields = get_field_names(Line)

    def has_add_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False


@admin.register(Order)
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
    list_filter = ("status", "payment_type")
    search_fields = ("user__email", "user__username")
    raw_id_fields = ("user", "application")
    inlines = [LineInline]

    def has_add_permission(self, request):  # noqa: ARG002, D102
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False

    def save_model(self, request, obj, form, change):  # noqa: ARG002
        """
        Saves object and logs change to object
        """
        obj.save_and_log(request.user)

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("user")

    @admin.display(
        description="User",
        ordering="user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        return obj.user.email

    @admin.display(description="Application")
    def application_link(self, obj):
        """Returns a link to the related application"""
        if not hasattr(obj, "application") or obj.application is None:
            return None
        return mark_safe(
            '<a href="{}">Application ({})</a>'.format(
                reverse(
                    "admin:applications_{}_change".format(
                        application_models.BootcampApplication._meta.model_name  # noqa: SLF001
                    ),
                    args=(obj.application.id,),
                ),
                obj.application.id,
            )
        )


@admin.register(OrderAudit)
class OrderAuditAdmin(admin.ModelAdmin):
    """Admin for OrderAudit"""

    model = OrderAudit
    readonly_fields = get_field_names(OrderAudit)

    def has_add_permission(self, request):  # noqa: ARG002, D102
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False


@admin.register(Receipt)
class ReceiptAdmin(TimestampedModelAdmin):
    """Admin for Receipt"""

    model = Receipt
    include_created_on_in_list = True
    readonly_fields = get_field_names(Receipt) + ["order_link"]  # noqa: RUF005
    list_display = ("id", "get_user_email", "order_link", "get_order_status")
    search_fields = ("order__user__email", "order__user__username")

    def has_add_permission(self, request):  # noqa: ARG002, D102
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("order__user")

    @admin.display(
        description="User",
        ordering="order__user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        if obj.order is None:
            return None
        return obj.order.user.email

    @admin.display(
        description="Status",
        ordering="order__status",
    )
    def get_order_status(self, obj):
        """Returns the order status"""
        if obj.order is None:
            return None
        return obj.order.status

    @admin.display(description="Order")
    def order_link(self, obj):
        """Returns a link to the related order"""
        if obj.order is None:
            return None
        return mark_safe(
            '<a href="{}">Order ({})</a>'.format(
                reverse(
                    "admin:ecommerce_{}_change".format(Order._meta.model_name),  # noqa: SLF001
                    args=(obj.order.id,),
                ),
                obj.order.id,
            )
        )


@admin.register(WireTransferReceipt)
class WireTransferReceiptAdmin(TimestampedModelAdmin):
    """Admin for WireTransferReceipt"""

    model = WireTransferReceipt
    include_created_on_in_list = True
    readonly_fields = get_field_names(WireTransferReceipt) + ["order_link"]  # noqa: RUF005
    list_display = ("id", "get_user_email", "order_link", "get_order_status")
    search_fields = ("order__user__email", "order__user__username")

    def has_add_permission(self, request):  # noqa: ARG002, D102
        return False

    def has_delete_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False

    def has_change_permission(self, request, obj=None):  # noqa: ARG002, D102
        return False

    def get_queryset(self, request):
        """Overrides base queryset"""
        return super().get_queryset(request).select_related("order__user")

    @admin.display(
        description="User",
        ordering="order__user__email",
    )
    def get_user_email(self, obj):
        """Returns the user email"""
        if obj.order is None:
            return None
        return obj.order.user.email

    @admin.display(
        description="Status",
        ordering="order__status",
    )
    def get_order_status(self, obj):
        """Returns the order status"""
        if obj.order is None:
            return None
        return obj.order.status

    @admin.display(description="Order")
    def order_link(self, obj):
        """Returns a link to the related order"""
        if obj.order is None:
            return None
        return mark_safe(
            '<a href="{}">Order ({})</a>'.format(
                reverse(
                    "admin:ecommerce_{}_change".format(Order._meta.model_name),  # noqa: SLF001
                    args=(obj.order.id,),
                ),
                obj.order.id,
            )
        )
