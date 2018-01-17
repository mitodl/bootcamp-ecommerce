"""Views for fluidreview"""
from rest_framework.response import Response
from rest_framework.views import APIView

from bootcamp.negotiations import IgnoreClientContentNegotiation
from fluidreview.api import FluidReviewException
from fluidreview.permissions import WebhookPermission
from fluidreview.models import WebhookRequest


class WebhookView(APIView):
    """
    Handle webhooks coming from FluidReview
    """
    permission_classes = (WebhookPermission,)
    authentication_classes = ()
    content_negotiation_class = IgnoreClientContentNegotiation

    def handle_exception(self, exc):
        """Raise any exception with request info instead of returning response with error status/message"""
        raise FluidReviewException(
            "REST Error (%s). BODY: %s, META: %s" % (exc, self.request.body, self.request.META)
        ) from exc

    def post(self, request):
        """Store webhook request for later processing"""
        WebhookRequest.objects.create(body=request.body)
        return Response()
