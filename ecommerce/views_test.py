"""Tests for ecommerce views"""
from unittest.mock import patch

from django.core.urlresolvers import (
    resolve,
    reverse,
)
from django.test import (
    override_settings,
    TestCase,
)
from rest_framework import status as statuses

from ecommerce.api_test import create_purchasable_klass
from ecommerce.serializers import PaymentSerializer
from profiles.factories import UserFactory


CYBERSOURCE_SECURITY_KEY = '🔑'
CYBERSOURCE_SECURE_ACCEPTANCE_URL = 'http://fake'
CYBERSOURCE_REFERENCE_PREFIX = 'fake'


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
            "total": "-1",
            "klass_id": 3,
        })
        assert resp.status_code == statuses.HTTP_400_BAD_REQUEST
        assert resp.json() == {
            "total": ["Ensure this value is greater than or equal to 0.01."]
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
                "total": klass.price,
                "klass_id": klass.klass_id,
            })
        assert resp.status_code == statuses.HTTP_200_OK
        assert resp.json() == {
            'payload': fake_payload,
            'url': CYBERSOURCE_SECURE_ACCEPTANCE_URL,
        }
        assert generate_cybersource_sa_payload_mock.call_count == 1
        generate_cybersource_sa_payload_mock.assert_any_call(fake_order, "http://testserver/")
        assert create_unfulfilled_order_mock.call_count == 1
        create_unfulfilled_order_mock.assert_any_call(user, klass.klass_id, klass.price)
