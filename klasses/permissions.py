"""
Permission classes for the bootcamps
"""

from django.contrib.auth.models import User
from django.http import Http404
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission

from backends.edxorg import EdxOrgOAuth2


class CanReadIfSelf(BasePermission):
    """
    Only the requester can view their own pay.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            raise Http404

        user = get_object_or_404(
            User,
            social_auth__uid=view.kwargs["username"],
            social_auth__provider=EdxOrgOAuth2.name,
        )

        # if the user is looking for their own profile, they're good
        if request.user == user:
            return True
        return False
