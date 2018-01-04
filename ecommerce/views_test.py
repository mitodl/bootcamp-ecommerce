"""Tests for ecommerce views"""
from unittest.mock import patch

import ddt
from django.core.urlresolvers import (
    resolve,
    reverse,
)
from django.test import (
    override_settings,
    TestCase,
)
import faker
from rest_framework import status as statuses

from ecommerce.api import make_reference_id
from ecommerce.api_test import (
    create_purchasable_klass,
    create_test_order,
)
from ecommerce.exceptions import EcommerceException
from ecommerce.models import (
    Order,
    OrderAudit,
    Receipt,
)
from ecommerce.serializers import PaymentSerializer
from fluidreview.api import FluidReviewException
from fluidreview.constants import WebhookParseStatus
from fluidreview.factories import WebhookRequestFactory
from profiles.factories import UserFactory


CYBERSOURCE_SECURITY_KEY = '🔑'
CYBERSOURCE_SECURE_ACCEPTANCE_URL = 'http://fake'
CYBERSOURCE_REFERENCE_PREFIX = 'fake'
FAKE = faker.Factory.create()


class PaymentTests(TestCase):
    """Tests for payment API"""

    def test_using_serializer_validation(self):
        """
        The view should use the serializer for validation
        """
        payment_url = reverse('create-payment')
        assert resolve(payment_url).func.view_class.serializer_class is PaymentSerializer

        # Make sure we haven't overridden something which would skip validation
        user = UserFactory.create()
        self.client.force_login(user)
        resp = self.client.post(payment_url, data={
            "payment_amount": "-1",
            "klass_key": 3,
        })
        assert resp.status_code == statuses.HTTP_400_BAD_REQUEST
        assert resp.json() == {
            "payment_amount": ["Ensure this value is greater than or equal to 0.01."]
        }

    def test_login_required(self):
        """Anonymous users are forbidden"""
        resp = self.client.post(reverse('create-payment'), data={})
        assert resp.status_code == statuses.HTTP_403_FORBIDDEN

    @override_settings(
        CYBERSOURCE_SECURITY_KEY=CYBERSOURCE_SECURITY_KEY,
        CYBERSOURCE_SECURE_ACCEPTANCE_URL=CYBERSOURCE_SECURE_ACCEPTANCE_URL,
        CYBERSOURCE_REFERENCE_PREFIX=CYBERSOURCE_REFERENCE_PREFIX,
    )
    def test_payment(self):
        """
        If a user POSTs to the payment API an unfulfilled order should be created
        """
        klass, user = create_purchasable_klass()
        self.client.force_login(user)
        fake_payload = "fake_payload"
        fake_order = 'fake_order'
        with patch(
            'ecommerce.views.generate_cybersource_sa_payload', autospec=True, return_value=fake_payload
        ) as generate_cybersource_sa_payload_mock, patch(
            'ecommerce.views.create_unfulfilled_order', autospec=True, return_value=fake_order
        ) as create_unfulfilled_order_mock:
            resp = self.client.post(reverse('create-payment'), data={
                "payment_amount": klass.price,
                "klass_key": klass.klass_key,
            })
        assert resp.status_code == statuses.HTTP_200_OK
        assert resp.json() == {
            'payload': fake_payload,
            'url': CYBERSOURCE_SECURE_ACCEPTANCE_URL,
        }
        assert generate_cybersource_sa_payload_mock.call_count == 1
        generate_cybersource_sa_payload_mock.assert_any_call(fake_order, "http://testserver/")
        assert create_unfulfilled_order_mock.call_count == 1
        create_unfulfilled_order_mock.assert_any_call(user, klass.klass_key, klass.price)


@override_settings(
    CYBERSOURCE_REFERENCE_PREFIX=CYBERSOURCE_REFERENCE_PREFIX,
    ECOMMERCE_EMAIL='ecommerce@example.com'
)
@ddt.ddt
class OrderFulfillmentViewTests(TestCase):
    """
    Tests for order fulfillment
    """
    @ddt.data(None, FluidReviewException)
    def test_order_fulfilled(self, side_effect):
        """
        Test the happy case
        """
        klass, user = create_purchasable_klass()
        user.profile.fluidreview_id = 999
        user.profile.save()
        payment = 123
        order = create_test_order(user, klass.klass_key, payment)
        WebhookRequestFactory(
            user_email=user.email,
            user_id=user.profile.fluidreview_id,
            award_id=klass.klass_key,
            status=WebhookParseStatus.SUCCEEDED
        )
        data_before = order.to_dict()

        data = {}
        for _ in range(5):
            data[FAKE.text()] = FAKE.text()

        data['req_reference_number'] = make_reference_id(order)
        data['decision'] = 'ACCEPT'
        with patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=True), patch(
            'ecommerce.views.MailgunClient.send_individual_email',
        ) as send_email, patch('fluidreview.api.FluidReviewAPI.put', side_effect=side_effect) as mockapi:
            resp = self.client.post(reverse('order-fulfillment'), data=data)

        assert len(resp.content) == 0
        assert resp.status_code == statuses.HTTP_200_OK
        order.refresh_from_db()
        assert order.status == Order.FULFILLED
        assert order.receipt_set.count() == 1
        assert order.receipt_set.first().data == data

        assert send_email.call_count == 0
        mockapi.assert_called_once()
        assert mockapi.call_args[1] == {'data': {'value': '{}.00'.format(payment)}}
        assert OrderAudit.objects.count() == 2
        order_audit = OrderAudit.objects.last()
        assert order_audit.order == order
        assert order_audit.data_before == data_before
        assert order_audit.data_after == order.to_dict()

    def test_missing_fields(self):
        """
        If CyberSource POSTs with fields missing, we should at least save it in a receipt.
        It is very unlikely for Cybersource to POST invalid data but it also provides a way to test
        that we save a Receipt in the event of an error.
        """
        data = {}
        for _ in range(5):
            data[FAKE.text()] = FAKE.text()
        with patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=True):
            try:
                # Missing fields from Cybersource POST will cause the KeyError.
                # In this test we just care that we saved the data in Receipt for later
                # analysis.
                self.client.post(reverse('order-fulfillment'), data=data)
            except KeyError:
                pass

        assert Order.objects.count() == 0
        assert Receipt.objects.count() == 1
        assert Receipt.objects.first().data == data

    @ddt.data(
        ('CANCEL', False),
        ('something else', True),
    )
    @ddt.unpack
    def test_not_accept(self, decision, should_send_email):
        """
        If the decision is not ACCEPT then the order should be marked as failed
        """
        klass, user = create_purchasable_klass()
        order = create_test_order(user, klass.klass_key, 123)

        data = {
            'req_reference_number': make_reference_id(order),
            'decision': decision,
        }
        with patch(
            'ecommerce.views.IsSignedByCyberSource.has_permission',
            return_value=True
        ), patch(
            'ecommerce.views.MailgunClient.send_individual_email',
        ) as send_email:
            resp = self.client.post(reverse('order-fulfillment'), data=data)
        assert resp.status_code == statuses.HTTP_200_OK
        assert len(resp.content) == 0
        order.refresh_from_db()
        assert Order.objects.count() == 1
        assert order.status == Order.FAILED

        if should_send_email:
            assert send_email.call_count == 1
            assert send_email.call_args[0] == (
                'Order fulfillment failed, decision={decision}'.format(decision='something else'),
                'Order fulfillment failed for order {order}'.format(order=order),
                'ecommerce@example.com',
            )
        else:
            assert send_email.call_count == 0

    def test_ignore_duplicate_cancel(self):
        """
        If the decision is CANCEL and we already have a duplicate failed order, don't change anything.
        """
        klass, user = create_purchasable_klass()
        order = create_test_order(user, klass.klass_key, 123)
        order.status = Order.FAILED
        order.save()

        data = {
            'req_reference_number': make_reference_id(order),
            'decision': 'CANCEL',
        }
        with patch(
            'ecommerce.views.IsSignedByCyberSource.has_permission',
            return_value=True
        ):
            resp = self.client.post(reverse('order-fulfillment'), data=data)
        assert resp.status_code == statuses.HTTP_200_OK

        assert Order.objects.count() == 1
        assert Order.objects.get(id=order.id).status == Order.FAILED

    @ddt.data(
        (Order.FAILED, 'ERROR'),
        (Order.FULFILLED, 'ERROR'),
        (Order.FULFILLED, 'SUCCESS'),
    )
    @ddt.unpack
    def test_error_on_duplicate_order(self, order_status, decision):
        """If there is a duplicate message (except for CANCEL), raise an exception"""
        klass, user = create_purchasable_klass()
        order = create_test_order(user, klass.klass_key, 123)
        order.status = order_status
        order.save()

        data = {
            'req_reference_number': make_reference_id(order),
            'decision': decision,
        }
        with patch(
            'ecommerce.views.IsSignedByCyberSource.has_permission',
            return_value=True
        ), self.assertRaises(EcommerceException) as ex:
            self.client.post(reverse('order-fulfillment'), data=data)

        assert Order.objects.count() == 1
        assert Order.objects.get(id=order.id).status == order_status

        assert ex.exception.args[0] == "Order {id} is expected to have status 'created'".format(
            id=order.id,
        )

    def test_no_permission(self):
        """
        If the permission class didn't give permission we shouldn't get access to the POST
        """
        with patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=False):
            resp = self.client.post(reverse('order-fulfillment'), data={})
        assert resp.status_code == statuses.HTTP_403_FORBIDDEN
