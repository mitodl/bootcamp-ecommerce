"""Views for bootcamp applications"""
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from applications.models import BootcampApplication
from applications.serializers import BootcampApplicationDetailSerializer, BootcampApplicationSerializer
from applications.api import get_or_create_bootcamp_application
from klasses.models import BootcampRun
from main.permissions import UserIsOwnerPermission


class BootcampApplicationViewset(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """
    View for fetching users' serialized bootcamp application(s)
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated, UserIsOwnerPermission,)
    owner_field = "user"

    def get_queryset(self):
        if self.action == "retrieve":
            return BootcampApplication.objects.prefetch_state_data()
        else:
            return BootcampApplication.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BootcampApplicationDetailSerializer
        elif self.action in {"list", "create"}:
            return BootcampApplicationSerializer
        raise MethodNotAllowed("Cannot perform the requested action.")

    def create(self, request, *args, **kwargs):
        bootcamp_run_id = request.data.get("bootcamp_run_id")
        if not bootcamp_run_id:
            raise ValidationError("Bootcamp run ID required.")
        if not BootcampRun.objects.filter(id=bootcamp_run_id).exists():
            return Response(
                data={"error": "Bootcamp does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        application, created = get_or_create_bootcamp_application(
            user=request.user,
            bootcamp_run_id=bootcamp_run_id
        )
        serializer_cls = self.get_serializer_class()
        return Response(
            data=serializer_cls(instance=application).data,
            status=(status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        )
