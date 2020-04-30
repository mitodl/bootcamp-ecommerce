"""jobma permission classes"""
from django.conf import settings

from rest_framework.permissions import BasePermission


class JobmaWebhookPermission(BasePermission):
    """Restrict access to jobma via access token"""

    def has_permission(self, request, view):
        header = request.headers.get("authorization", "")
        if header.startswith("Token "):
            token = header[len("Token "):]
            return token == settings.JOBMA_WEBHOOK_ACCESS_TOKEN
        return False
