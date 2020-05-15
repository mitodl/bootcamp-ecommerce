"""Views for bootcamp applications"""
from django.core.exceptions import ImproperlyConfigured
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from applications.models import BootcampApplication
from applications.serializers import BootcampApplicationDetailSerializer, BootcampApplicationListSerializer
from main.permissions import UserIsOwnerPermission


class BootcampApplicationViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    View for fetching users' serialized bootcamp application(s)
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwnerPermission,)
    queryset = BootcampApplication.objects.prefetch_state_data()
    owner_field = "user"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BootcampApplicationDetailSerializer
        elif self.action == "list":
            return BootcampApplicationListSerializer
        raise ImproperlyConfigured("Cannot perform the requested action.")
