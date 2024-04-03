"""views for bootcamps"""

from django.db.models.functions import Now
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from klasses.serializers import BootcampRunSerializer
from klasses.models import BootcampRun, BootcampRunEnrollment


class BootcampViewSet(ListModelMixin, GenericViewSet):
    """Viewset for bootcamps"""

    permission_classes = (IsAuthenticated,)
    serializer_class = BootcampRunSerializer

    def get_queryset(self):
        """Make a queryset which optionally shows what runs are available for enrollment"""
        user = self.request.user
        has_enrollments = BootcampRunEnrollment.objects.filter(
            user=user, active=True
        ).exists()
        queryset = BootcampRun.objects.select_related("bootcamp")
        if not user.profile.can_skip_application_steps and not has_enrollments:
            queryset = queryset.filter(allows_skipped_steps=False)

        if self.request.query_params.get("available") == "true":
            queryset = queryset.filter(start_date__gt=Now()).exclude(
                applications__user=user
            )
        return queryset.order_by("id")
