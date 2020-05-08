"""views for jobma"""
import logging

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from jobma.models import Interview
from jobma.permissions import JobmaWebhookPermission


log = logging.getLogger(__name__)


class JobmaWebhookView(GenericAPIView):
    """An endpoint for Jobma to publish the interview status"""
    permission_classes = (JobmaWebhookPermission,)
    lookup_field = "pk"
    queryset = Interview.objects.all()

    def put(self, request, *args, **kwargs):
        """Update the Jobma interview status result"""
        status = request.data["status"]

        interview = self.get_object()
        interview.status = status
        interview.save_and_log(None)

        return Response(status=200)