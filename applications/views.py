"""Views for bootcamp applications"""
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from applications.serializers import BootcampApplicationDetailSerializer, BootcampApplicationSerializer
from applications.api import get_or_create_bootcamp_application, set_submission_review_status
from applications.models import BootcampApplication, ApplicationStepSubmission
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
            return BootcampApplication.objects.filter(user=self.request.user).all()

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


class ReviewSubmissionView(UpdateAPIView):
    """
    Admin view for setting review status on application submission
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAdminUser,)
    lookup_field = "pk"
    queryset = ApplicationStepSubmission.objects.all()

    def patch(self, request, *args, **kwargs):
        """
        Update review status for application submission
        """
        submission = self.get_object()
        review_status = request.data["review_status"]
        set_submission_review_status(submission, review_status)

        return Response(status=status.HTTP_200_OK)
