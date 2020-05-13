"""Views for ecommerce"""
from decimal import Decimal
import logging

from django.conf import settings
from django.urls import reverse
from rest_framework import status as statuses
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.api import (
    complete_successful_order,
    create_unfulfilled_order,
    generate_cybersource_sa_payload,
    get_new_order_by_reference_number,
    handle_rejected_order,
)
from ecommerce.constants import (
    CYBERSOURCE_DECISION_ACCEPT,
    CYBERSOURCE_DECISION_CANCEL,
)
from ecommerce.exceptions import EcommerceException
from ecommerce.models import (
    Order,
    Receipt,
)
from ecommerce.permissions import IsSignedByCyberSource
from ecommerce.serializers import PaymentSerializer
from fluidreview.api import post_payment as post_payment_fluid
from hubspot.task_helpers import sync_hubspot_deal_from_order
from klasses.constants import ApplicationSource
from smapply.api import post_payment as post_payment_sma


log = logging.getLogger(__name__)


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
        payment_amount = Decimal(serializer.data['payment_amount'])
        run_key = serializer.data['run_key']

        order = create_unfulfilled_order(self.request.user, run_key, payment_amount)

        # Sync order data with hubspot
        sync_hubspot_deal_from_order(order)

        redirect_url = self.request.build_absolute_uri(reverse('pay'))

        return Response({
            'payload': generate_cybersource_sa_payload(order, redirect_url),
            'url': settings.CYBERSOURCE_SECURE_ACCEPTANCE_URL,
        })


class OrderFulfillmentView(APIView):
    """
    View for order fulfillment API. This API is special in that only CyberSource should talk to it.
    Instead of authenticating with OAuth or via session this looks at the signature of the message
    to verify authenticity.
    """

    authentication_classes = ()
    permission_classes = (IsSignedByCyberSource, )

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Confirmation from CyberSource which fulfills an existing Order.
        """
        # First, save this information in a receipt
        receipt = Receipt.objects.create(data=request.data)

        # Link the order with the receipt if we can parse it
        reference_number = request.data['req_reference_number']
        order = get_new_order_by_reference_number(reference_number)
        receipt.order = order
        receipt.save()

        decision = request.data['decision']
        if order.status == Order.FAILED and decision == CYBERSOURCE_DECISION_CANCEL:
            # This is a duplicate message, ignore since it's already handled
            return Response(status=statuses.HTTP_200_OK)
        elif order.status != Order.CREATED:
            raise EcommerceException("Order {} is expected to have status 'created'".format(order.id))

        if decision != CYBERSOURCE_DECISION_ACCEPT:
            handle_rejected_order(order=order, decision=decision)
        else:
            complete_successful_order(order)

        try:
            if order.get_bootcamp_run().source == ApplicationSource.FLUIDREVIEW:
                post_payment_fluid(order)
            else:
                post_payment_sma(order)
        except:  # pylint: disable=bare-except
            log.exception('Error occurred posting payment to FluidReview for order %s', order)

        # Sync order data with hubspot
        sync_hubspot_deal_from_order(order)

        # The response does not matter to CyberSource
        return Response(status=statuses.HTTP_200_OK)
