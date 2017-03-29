"""Views for ecommerce"""
from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from ecommerce.api import (
    create_unfulfilled_order,
    generate_cybersource_sa_payload,
)
from ecommerce.serializers import PaymentSerializer


class PaymentView(CreateAPIView):
    """
    View for payment API. This creates an Order in our system and provides a dictionary to send to Cybersource.
    """
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer

    def post(self, request, *args, **kwargs):
        """
        Create an unfulfilled order and return a response for it.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        total = Decimal(serializer.data['total'])
        klass_id = serializer.data['klass_id']

        order = create_unfulfilled_order(self.request.user, klass_id, total)
        redirect_url = self.request.build_absolute_uri(reverse('bootcamp-index'))

        return Response({
            'payload': generate_cybersource_sa_payload(order, redirect_url),
            'url': settings.CYBERSOURCE_SECURE_ACCEPTANCE_URL,
        })
