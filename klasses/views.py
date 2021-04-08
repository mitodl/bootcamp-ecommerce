"""views for bootcamps"""
from django.db.models.functions import Now
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from applications.constants import AppStates
from applications.models import BootcampApplication
from klasses.serializers import BootcampRunSerializer
from klasses.models import BootcampRun


class BootcampViewSet(ListModelMixin, GenericViewSet):
    """Viewset for bootcamps"""

    permission_classes = (IsAuthenticated,)
    serializer_class = BootcampRunSerializer

    def get_queryset(self):
        """Make a queryset which optionally shows what runs are available for enrollment"""
        user = self.request.user
        complete_applications = BootcampApplication.objects.filter(
            user=user, state=AppStates.COMPLETE.value
        )
        # if user is an alumni or have already bought a course, show them all the bootcamps
        if user.profile.can_skip_application_steps or complete_applications.exists():
            queryset = BootcampRun.objects.all().select_related("bootcamp")
        else:
            queryset = BootcampRun.objects.filter(
                allows_skipped_steps=False
            ).select_related("bootcamp")
        if self.request.query_params.get("available") == "true":
            queryset = queryset.filter(start_date__gt=Now()).exclude(
                applications__user=user
            )
        return queryset.order_by("id")
