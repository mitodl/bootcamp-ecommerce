"""
Views for Klasses app
"""
import logging

from django.contrib.auth.models import User
from rest_framework import (
    authentication,
    permissions,
)
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from backends.edxorg import EdxOrgOAuth2
from klasses.api import serialize_user_klasses, serialize_user_klass
from klasses.models import Klass
from klasses.permissions import CanReadIfSelf

log = logging.getLogger(__name__)


class UserKlassList(APIView):
    """
    Class based view for user klass list view.
    """
    authentication_classes = (
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
        CanReadIfSelf,
    )

    def get(self, request, username, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Returns information about the payments for the user in all the klasses she is allowed to pay.
        """
        user = get_object_or_404(
            User,
            social_auth__uid=username,
            social_auth__provider=EdxOrgOAuth2.name
        )

        return Response(serialize_user_klasses(user=user))


class UserKlassDetail(GenericAPIView):
    """
    Class based view for user klass view.
    """
    authentication_classes = (
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
        CanReadIfSelf,
    )
    lookup_field = "klass_key"
    lookup_url_kwarg = "klass_key"
    queryset = Klass.objects.all()

    def get(self, request, username, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Returns information about the payments for the user in the specified klass.
        """
        user = get_object_or_404(
            User,
            social_auth__uid=username,
            social_auth__provider=EdxOrgOAuth2.name
        )
        klass = self.get_object()
        return Response(serialize_user_klass(user=user, klass=klass))
