"""User views"""

import pycountry
from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from mitol.common.utils import now_in_utc

from main.permissions import UserIsOwnerPermission
from profiles.models import ChangeEmailRequest
from profiles.serializers import (
    UserSerializer,
    CountrySerializer,
    ChangeEmailRequestCreateSerializer,
    ChangeEmailRequestUpdateSerializer,
)

User = get_user_model()


class UserRetrieveViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """User retrieve viewsets"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserIsOwnerPermission]
    required_scopes = ["user"]


class CurrentUserRetrieveUpdateViewSet(
    mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """User retrieve and update viewsets for the current user"""

    # NOTE: this is a separate viewset from UserRetrieveViewSet because of the differences in permission requirements
    serializer_class = UserSerializer
    permission_classes = []

    def get_object(self):
        """Returns the current request user"""
        # NOTE: this may be a logged in or anonymous user
        return self.request.user


class ChangeEmailRequestViewSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """Viewset for creating and updating email change requests"""

    lookup_field = "code"

    def get_permissions(self):
        permission_classes = []
        if self.action == "create":
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return a queryset of valid pending requests"""
        return ChangeEmailRequest.objects.filter(
            expires_on__gt=now_in_utc(), confirmed=False
        )

    def get_serializer_class(self):
        if self.action == "create":
            return ChangeEmailRequestCreateSerializer
        elif self.action == "partial_update":
            return ChangeEmailRequestUpdateSerializer


class CountriesStatesViewSet(viewsets.ViewSet):
    """Retrieve viewset of countries, with states/provinces for US and Canada"""

    permission_classes = []

    def list(self, request):  # pylint:disable=unused-argument
        """Get generator for countries/states list"""
        queryset = sorted(list(pycountry.countries), key=lambda country: country.name)
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)
