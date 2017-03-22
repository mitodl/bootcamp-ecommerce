"""
Test for ecommerce functions
"""
from base64 import b64encode
import hashlib
import hmac

from django.test import (
    override_settings,
    TestCase,
)

from ecommerce.api import (
    generate_cybersource_sa_signature,
    make_reference_id,
)
from ecommerce.factories import OrderFactory


CYBERSOURCE_ACCESS_KEY = 'access'
CYBERSOURCE_PROFILE_ID = 'profile'
CYBERSOURCE_SECURITY_KEY = 'security'
CYBERSOURCE_REFERENCE_PREFIX = 'prefix'


@override_settings(
    CYBERSOURCE_ACCESS_KEY=CYBERSOURCE_ACCESS_KEY,
    CYBERSOURCE_PROFILE_ID=CYBERSOURCE_PROFILE_ID,
    CYBERSOURCE_SECURITY_KEY=CYBERSOURCE_SECURITY_KEY,
)
class CybersourceTests(TestCase):
    """
    Tests for generate_cybersource_sa_signature
    """
    def test_valid_signature(self):
        """
        Signature is made up of a ordered key value list signed using HMAC 256 with a security key
        """
        payload = {
            'x': 'y',
            'abc': 'def',
            'key': 'value',
            'signed_field_names': 'abc,x',
        }
        signature = generate_cybersource_sa_signature(payload)

        message = ','.join('{}={}'.format(key, payload[key]) for key in ['abc', 'x'])

        digest = hmac.new(
            CYBERSOURCE_SECURITY_KEY.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()

        assert b64encode(digest).decode('utf-8') == signature


@override_settings(CYBERSOURCE_REFERENCE_PREFIX=CYBERSOURCE_REFERENCE_PREFIX)
class ReferenceNumberTests(TestCase):
    """
    Tests for make_reference_id
    """

    def test_make_reference_id(self):
        """
        make_reference_id should concatenate the reference prefix and the order id
        """
        order = OrderFactory.create()
        assert "BOOTCAMP-{}-{}".format(CYBERSOURCE_REFERENCE_PREFIX, order.id) == make_reference_id(order)
