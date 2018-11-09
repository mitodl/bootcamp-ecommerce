"""Views for smapply"""
from rest_framework.response import Response
from rest_framework.views import APIView

from bootcamp.negotiations import IgnoreClientContentNegotiation
from smapply.api import SMApplyException
from smapply.permissions import WebhookPermission
from smapply.models import WebhookRequestSMA


class WebhookView(APIView):
    """
    Handle webhooks coming from FluidReview
    """
    permission_classes = (WebhookPermission,)
    authentication_classes = ()
    content_negotiation_class = IgnoreClientContentNegotiation

    def handle_exception(self, exc):
        """Raise any exception with request info instead of returning response with error status/message"""
        raise SMApplyException(
            "REST Error (%s). BODY: %s, META: %s" % (exc, self.request.body, self.request.META)
        ) from exc

    def post(self, request):
        """Store webhook request for later processing"""
        WebhookRequestSMA.objects.create(body=request.body)
        return Response()
