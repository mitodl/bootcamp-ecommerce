"""jobma permission classes"""
import logging

from django.conf import settings

from rest_framework.permissions import BasePermission


log = logging.getLogger(__name__)


class JobmaWebhookPermission(BasePermission):
    """Restrict access to jobma via access token"""

    def has_permission(self, request, view):
        if not settings.JOBMA_WEBHOOK_ACCESS_TOKEN:
            log.error("JOBMA_WEBHOOK_ACCESS_TOKEN not set")
            return False
        header = request.headers.get("authorization", "")
        if header.startswith("Bearer "):
            token = header[len("Bearer ") :]

            return token == settings.JOBMA_WEBHOOK_ACCESS_TOKEN
        return False
