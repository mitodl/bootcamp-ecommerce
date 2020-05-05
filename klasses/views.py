"""
Views for bootcamps
"""
import logging

from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import (
    authentication,
    permissions,
)
from rest_framework.generics import (
    RetrieveAPIView,
    GenericAPIView,
    get_object_or_404
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from backends.edxorg import EdxOrgOAuth2
from main.serializers import serialize_maybe_user
from klasses.api import serialize_user_bootcamp_runs, serialize_user_bootcamp_run
from klasses.models import BootcampRun
from klasses.permissions import CanReadIfSelf
from ecommerce.models import Line

log = logging.getLogger(__name__)


class UserBootcampRunList(APIView):
    """
    Class based view for user bootcamp run list view.
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
        Returns serialized bootcamp runs and payments for all runs that a user can pay for.
        """
        user = get_object_or_404(
            User,
            social_auth__uid=username,
            social_auth__provider=EdxOrgOAuth2.name
        )

        return Response(serialize_user_bootcamp_runs(user=user))


class UserBootcampRunDetail(GenericAPIView):
    """
    Class based view for user bootcamp run view.
    """
    authentication_classes = (
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
        CanReadIfSelf,
    )
    lookup_field = "run_key"
    lookup_url_kwarg = "run_key"
    queryset = BootcampRun.objects.all()

    def get(self, request, username, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Returns a serialized bootcamp run and payment for a user
        """
        user = get_object_or_404(
            User,
            social_auth__uid=username,
            social_auth__provider=EdxOrgOAuth2.name
        )
        bootcamp_run = self.get_object()
        return Response(serialize_user_bootcamp_run(user=user, bootcamp_run=bootcamp_run))


class UserBootcampRunStatement(RetrieveAPIView):
    """
    View class for a user's bootcamp run payment statement
    """
    authentication_classes = (
        authentication.SessionAuthentication,
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )
    lookup_field = "run_key"
    lookup_url_kwarg = "run_key"
    queryset = BootcampRun.objects.all()
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        """
        Fetches a user's bootcamp run payment information and renders their statement
        (or raises a 404 if they have no payments for the specified bootcamp run)
        """
        bootcamp_run = self.get_object()
        if Line.for_user_bootcamp_run(request.user, bootcamp_run.run_key).count() == 0:
            raise Http404
        return Response(
            {
                "user": serialize_maybe_user(request.user),
                "bootcamp_run": serialize_user_bootcamp_run(user=request.user, bootcamp_run=bootcamp_run)
            },
            template_name='bootcamp/statement.html'
        )
