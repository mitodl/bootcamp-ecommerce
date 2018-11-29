"""Admin interface for smapply"""
from django.contrib import admin

from bootcamp.utils import get_field_names
from smapply.models import WebhookRequestSMA, OAuthTokenSMA


class WebhookRequestSMAAdmin(admin.ModelAdmin):
    """Admin for WebhookRequestSMA"""
    model = WebhookRequestSMA
    readonly_fields = get_field_names(WebhookRequestSMA)
    ordering = ('-created_on',)
    list_filter = ('award_id', 'status')
    search_fields = ('user_id', 'submission_id')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OAuthTokenSMAAdmin(admin.ModelAdmin):
    """Admin for OAuthTokenSMA"""
    model = OAuthTokenSMA


admin.site.register(WebhookRequestSMA, WebhookRequestSMAAdmin)
admin.site.register(OAuthTokenSMA, OAuthTokenSMAAdmin)
