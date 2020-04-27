"""Admin interface for fluidreview"""
from django.contrib import admin

from main.utils import get_field_names
from fluidreview.models import WebhookRequest, OAuthToken


class WebhookRequestAdmin(admin.ModelAdmin):
    """Admin for WebhookRequest"""
    model = WebhookRequest
    readonly_fields = get_field_names(WebhookRequest)
    ordering = ('-created_on',)
    list_filter = ('award_id', 'status')
    search_fields = ('user_email', 'user_id', 'submission_id')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OAuthTokenAdmin(admin.ModelAdmin):
    """Admin for OAuthToken"""
    model = OAuthToken


admin.site.register(WebhookRequest, WebhookRequestAdmin)
admin.site.register(OAuthToken, OAuthTokenAdmin)
