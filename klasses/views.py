"""views for bootcamps"""
from django.db.models import Q
from django.db.models.functions import Now
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from klasses.serializers import BootcampRunSerializer
from klasses.models import BootcampRun


class BootcampViewSet(ListModelMixin, GenericViewSet):
    """Viewset for bootcamps"""
    permission_classes = (IsAuthenticated,)
    serializer_class = BootcampRunSerializer

    def get_queryset(self):
        """Make a queryset which optionally shows what runs are available for enrollment"""
        queryset = BootcampRun.objects.all().select_related("bootcamp")
        if self.request.query_params.get("available") == "true":
            queryset = queryset.filter(start_date__lt=Now()).exclude(applications__user=self.request.user)
        return queryset.order_by("id")
