"""
Test for ecommerce functions
"""
from base64 import b64encode
from datetime import datetime
import hashlib
import hmac
from unittest.mock import (
    MagicMock,
    patch,
)

import ddt
from django.test import (
    override_settings,
    TestCase,
)
import pytz
from rest_framework.exceptions import ValidationError

from backends.pipeline_api import EdxOrgOAuth2
from ecommerce.api import (
    create_unfulfilled_order,
    generate_cybersource_sa_payload,
    generate_cybersource_sa_signature,
    get_new_order_by_reference_number,
    get_total_paid,
    ISO_8601_FORMAT,
    make_reference_id,
)
from ecommerce.exceptions import (
    EcommerceException,
    ParseException,
)
from ecommerce.factories import LineFactory
from ecommerce.models import (
    Order,
    OrderAudit,
)
from klasses.factories import InstallmentFactory
from profiles.factories import UserFactory, ProfileFactory


def create_purchasable_klass():
    """
    Creates a purchasable klass and an associated user. Klass price is at least $200, in two installments
    """
    installment_1 = InstallmentFactory.create(amount=200)
    InstallmentFactory.create(klass=installment_1.klass)
    profile = ProfileFactory.create()
    user = profile.user
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid="{}_edx".format(user.username),
    )
    return installment_1.klass, user


@ddt.ddt
class PurchasableTests(TestCase):
    """
    Tests for create_unfulfilled_order
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.klass, cls.user = create_purchasable_klass()

    def test_too_much(self):
        """
        An order cannot exceed the total amount for the klass
        """
        LineFactory.create(
            order__status=Order.FULFILLED,
            order__user=self.user,
            klass_id=self.klass.klass_id,
            order__total_price_paid=self.klass.price - 10
        )

        with self.assertRaises(ValidationError) as ex:
            # payment is $15 here but there is only $10 left to pay
            total = 15
            create_unfulfilled_order(self.user, self.klass.klass_id, total)

        message = (
            "Payment of ${total} plus already paid ${already_paid} for {klass} would be"
            " greater than total price of ${klass_price}".format(
                total=total,
                already_paid=self.klass.price - 10,
                klass=self.klass.title,
                klass_price=self.klass.price,
            )
        )
        assert ex.exception.args[0] == message

    @ddt.data(0, -1.23)
    def test_less_or_equal_to_zero(self, total):
        """
        An order may not have a negative or zero price
        """
        with self.assertRaises(ValidationError) as ex:
            create_unfulfilled_order(self.user, self.klass.klass_id, total)

        assert ex.exception.args[0] == 'Payment is less than or equal to zero'

    def test_create_order(self):  # pylint: disable=too-many-locals
        """
        Create Order from a purchasable klass
        """
        payment = 123
        order = create_unfulfilled_order(self.user, self.klass.klass_id, payment)

        assert Order.objects.count() == 1
        assert order.status == Order.CREATED
        assert order.total_price_paid == payment
        assert order.user == self.user

        assert order.line_set.count() == 1
        line = order.line_set.first()
        assert line.klass_id == self.klass.klass_id
        assert line.description == 'Installment for {}'.format(self.klass.title)
        assert line.price == payment

        assert OrderAudit.objects.count() == 1
        order_audit = OrderAudit.objects.first()
        assert order_audit.order == order
        assert order_audit.data_after == order.to_dict()

        # data_before only has modified_at different, since we only call save_and_log
        # after Order is already created
        data_before = order_audit.data_before
        dict_before = order.to_dict()
        del data_before['updated_on']
        del dict_before['updated_on']
        assert data_before == dict_before


class GetPaidTests(TestCase):
    """Tests for get_total_paid"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.klass, cls.user = create_purchasable_klass()
        cls.payment = 123
        order = create_unfulfilled_order(cls.user, cls.klass.klass_id, cls.payment)
        order.status = Order.FULFILLED
        order.save()

    def test_multiple_payments(self):
        """
        get_total_paid should look through all fulfilled orders for the payment for a particular user
        """
        # Multiple payments should be added together
        next_payment = 50
        order = create_unfulfilled_order(self.user, self.klass.klass_id, next_payment)
        order.status = Order.FULFILLED
        order.save()
        assert get_total_paid(self.user, self.klass.klass_id) == self.payment + next_payment

    def test_other_user(self):
        """other_user's payments shouldn't affect user"""
        other_user = UserFactory.create()
        assert get_total_paid(other_user, self.klass.klass_id) == 0

    def test_skip_unfulfilled(self):
        """Unfulfilled orders should be ignored"""
        create_unfulfilled_order(self.user, self.klass.klass_id, 45)
        assert get_total_paid(self.user, self.klass.klass_id) == self.payment

    def test_skip_other_klass(self):
        """Orders for other klasses should be ignored"""
        other_klass, other_user = create_purchasable_klass()
        other_order = create_unfulfilled_order(other_user, other_klass.klass_id, 50)
        other_order.status = Order.FULFILLED
        other_order.save()

        assert get_total_paid(self.user, self.klass.klass_id) == self.payment

    def test_no_payments(self):
        """If there are no payments get_total_paid should return 0"""
        Order.objects.all().update(status=Order.REFUNDED)
        assert get_total_paid(self.user, self.klass.klass_id) == 0


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
    Tests for generate_cybersource_sa_payload and generate_cybersource_sa_signature
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

    def test_signed_payload(self):
        """
        A valid payload should be signed appropriately
        """
        klass, user = create_purchasable_klass()
        payment = 123.45
        order = create_unfulfilled_order(user, klass.klass_id, payment)
        username = 'username'
        transaction_uuid = 'hex'

        now = datetime.now(tz=pytz.UTC)
        now_mock = MagicMock(return_value=now)

        with patch('ecommerce.api.get_social_username', autospec=True, return_value=username):
            with patch('ecommerce.api.datetime', autospec=True, now=now_mock):
                with patch('ecommerce.api.uuid.uuid4', autospec=True, return_value=MagicMock(hex=transaction_uuid)):
                    payload = generate_cybersource_sa_payload(order, 'dashboard_url')
        signature = payload.pop('signature')
        assert generate_cybersource_sa_signature(payload) == signature
        signed_field_names = payload['signed_field_names'].split(',')
        assert signed_field_names == sorted(payload.keys())

        assert payload == {
            'access_key': CYBERSOURCE_ACCESS_KEY,
            'amount': str(order.total_price_paid),
            'consumer_id': username,
            'currency': 'USD',
            'item_0_code': 'klass',
            'item_0_name': '{}'.format(klass.title),
            'item_0_quantity': 1,
            'item_0_sku': '{}'.format(klass.klass_id),
            'item_0_tax_amount': '0',
            'item_0_unit_price': str(order.total_price_paid),
            'line_item_count': 1,
            'locale': 'en-us',
            'override_custom_cancel_page': 'dashboard_url?status=cancel',
            'override_custom_receipt_page': 'dashboard_url?status=receipt',
            'reference_number': make_reference_id(order),
            'profile_id': CYBERSOURCE_PROFILE_ID,
            'signed_date_time': now.strftime(ISO_8601_FORMAT),
            'signed_field_names': ','.join(signed_field_names),
            'transaction_type': 'sale',
            'transaction_uuid': transaction_uuid,
            'unsigned_field_names': '',
            'merchant_defined_data1': 'bootcamp',
            'merchant_defined_data2': '{}'.format(klass.bootcamp.title),
            'merchant_defined_data3': 'klass',
            'merchant_defined_data4': '{}'.format(klass.title),
            'merchant_defined_data5': '{}'.format(klass.klass_id),
            'merchant_defined_data6': 'learner',
            'merchant_defined_data7': '{}'.format(order.user.profile.name),
            'merchant_defined_data8': '{}'.format(order.user.email),
        }
        now_mock.assert_called_with(tz=pytz.UTC)


@ddt.ddt
@override_settings(CYBERSOURCE_REFERENCE_PREFIX=CYBERSOURCE_REFERENCE_PREFIX)
class ReferenceNumberTests(TestCase):
    """
    Tests for make_reference_id and get_new_order_by_reference_number
    """

    def test_make_reference_id(self):
        """
        make_reference_id should concatenate the reference prefix and the order id
        """
        klass, user = create_purchasable_klass()
        order = create_unfulfilled_order(user, klass.klass_id, 123)
        assert "BOOTCAMP-{}-{}".format(CYBERSOURCE_REFERENCE_PREFIX, order.id) == make_reference_id(order)

    def test_get_new_order_by_reference_number(self):
        """
        get_new_order_by_reference_number returns an Order with status created
        """
        klass, user = create_purchasable_klass()
        order = create_unfulfilled_order(user, klass.klass_id, 123)
        same_order = get_new_order_by_reference_number(make_reference_id(order))
        assert same_order.id == order.id

    @ddt.data(
        ("XYZ-1-3", "Reference number must start with BOOTCAMP-"),
        ("BOOTCAMP-no_dashes_here", "Unable to find order number in reference number"),
        ("BOOTCAMP-something-NaN", "Unable to parse order number"),
        ("BOOTCAMP-not_matching-3", "CyberSource prefix doesn't match"),
    )
    @ddt.unpack
    def test_parse(self, reference_number, exception_message):
        """
        Test parse errors are handled well
        """
        with self.assertRaises(ParseException) as ex:
            get_new_order_by_reference_number(reference_number)
        assert ex.exception.args[0] == exception_message

    def test_status(self):
        """
        get_order_by_reference_number should only get orders with status=CREATED
        """
        klass, user = create_purchasable_klass()
        order = create_unfulfilled_order(user, klass.klass_id, 123)

        order.status = Order.FAILED
        order.save()

        with self.assertRaises(EcommerceException) as ex:
            # change order number to something not likely to already exist in database
            order.id = 98765432
            assert not Order.objects.filter(id=order.id).exists()
            get_new_order_by_reference_number(make_reference_id(order))
        assert ex.exception.args[0] == "Unable to find order {}".format(order.id)
