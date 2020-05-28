"""
Admin views for ecommerce models
"""

from django.contrib import admin

from main.utils import get_field_names
from ecommerce.models import Line, Order, OrderAudit, Receipt


class LineAdmin(admin.ModelAdmin):
    """Admin for Line"""

    model = Line

    readonly_fields = get_field_names(Line)
    list_display = ("description", "run_key", "price", "order")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OrderAdmin(admin.ModelAdmin):
    """Admin for Order"""

    model = Order

    readonly_fields = [name for name in get_field_names(Order) if name != "status"]
    list_display = (
        "id",
        "user",
        "status",
        "line_description",
        "run_title",
        "application",
    )
    list_filter = ("status",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        """
        Saves object and logs change to object
        """
        obj.save_and_log(request.user)


class OrderAuditAdmin(admin.ModelAdmin):
    """Admin for OrderAudit"""

    model = OrderAudit
    readonly_fields = get_field_names(OrderAudit)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ReceiptAdmin(admin.ModelAdmin):
    """Admin for Receipt"""

    model = Receipt
    readonly_fields = get_field_names(Receipt)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Line, LineAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderAudit, OrderAuditAdmin)
admin.site.register(Receipt, ReceiptAdmin)
