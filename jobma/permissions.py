"""jobma permission classes"""
import logging

from django.conf import settings

from rest_framework.permissions import BasePermission


log = logging.getLogger(__name__)


class JobmaWebhookPermission(BasePermission):
    """Restrict access to jobma via access token"""

    def has_permission(self, request, view):
        header = request.headers.get("authorization", "")
        if header.startswith("Token "):
            token = header[len("Token "):]
            if token == settings.JOBMA_WEBHOOK_ACCESS_TOKEN:
                return True
            else:
                log.error("Token found but did not match")
                return False
        log.error("No token found in authorization")
        return False
