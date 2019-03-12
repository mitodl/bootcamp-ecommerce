"""
Authentication classes for FluidReview
"""
from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework.permissions import BasePermission


class WebhookPermission(BasePermission):
    """
    Verify that the authentication token is correct
    """
    def has_permission(self, request, view):
        """Check the auth token"""
        try:
            print(request.META)
            token = request.META['HTTP_AUTHORIZATION']
        except KeyError:
            return False
        expected = 'Basic {}'.format(settings.SMAPPLY_WEBHOOK_AUTH_TOKEN)
        return constant_time_compare(token, expected)
