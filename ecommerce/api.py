"""
Functions for ecommerce
"""
from base64 import b64encode
from datetime import datetime
from decimal import Decimal
import hashlib
import hmac
import logging
import uuid

from django.conf import settings
from django.db import transaction
from django.db.models.aggregates import Sum
import pytz
from rest_framework.exceptions import ValidationError

from backends.utils import get_social_username
from main.utils import remove_html_tags
from ecommerce.exceptions import (
    EcommerceException,
    ParseException,
)
from ecommerce.models import (
    Line,
    Order,
)
from klasses.bootcamp_admissions_client import BootcampAdmissionClient
from klasses.models import Klass


ISO_8601_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
log = logging.getLogger(__name__)
_REFERENCE_NUMBER_PREFIX = 'BOOTCAMP-'


def get_total_paid(user, klass_key):
    """
    Get total paid for a klass for a user
    Args:
        user (User):
            The purchaser of the klass
        klass_key (int):
            A klass key, a class within a bootcamp

    Returns:
        Decimal: The total amount paid by a user for a klass
    """
    return Line.objects.filter(
        order__status=Order.FULFILLED,
        order__user=user,
        klass_key=klass_key,
    ).aggregate(price=Sum('price'))['price'] or Decimal(0)


@transaction.atomic
def create_unfulfilled_order(user, klass_key, payment_amount):
    """
    Create a new Order which is not fulfilled for a klass.

    Args:
        user (User):
            The purchaser of the klass
        klass_key (int):
            A klass key, a class within a bootcamp
        payment_amount (Decimal): The payment of the user
    Returns:
        Order: A newly created Order for the klass
    """
    payment_amount = Decimal(payment_amount)
    try:
        klass = Klass.objects.get(klass_key=klass_key)
    except Klass.DoesNotExist:
        # In the near future we should do other checking here based on information from Bootcamp REST API
        raise ValidationError("Incorrect klass key {}".format(klass_key))

    bootcamp_client = BootcampAdmissionClient(user)
    if not bootcamp_client.can_pay_klass(klass_key):
        raise ValidationError("User is unable to pay for klass {}".format(klass_key))

    if payment_amount <= 0:
        raise ValidationError("Payment is less than or equal to zero")

    order = Order.objects.create(
        status=Order.CREATED,
        total_price_paid=payment_amount,
        user=user,
    )
    Line.objects.create(
        order=order,
        klass_key=klass_key,
        description='Installment for {}'.format(klass.title),
        price=payment_amount,
    )
    order.save_and_log(user)
    return order


def generate_cybersource_sa_signature(payload):
    """
    Generate an HMAC SHA256 signature for the CyberSource Secure Acceptance payload

    Args:
        payload (dict): The payload to be sent to CyberSource
    Returns:
        str: The signature
    """
    # This is documented in certain CyberSource sample applications:
    # http://apps.cybersource.com/library/documentation/dev_guides/Secure_Acceptance_SOP/html/wwhelp/wwhimpl/js/html/wwhelp.htm#href=creating_profile.05.6.html
    keys = payload['signed_field_names'].split(',')
    message = ','.join('{}={}'.format(key, payload[key]) for key in keys)

    digest = hmac.new(
        settings.CYBERSOURCE_SECURITY_KEY.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256,
    ).digest()

    return b64encode(digest).decode('utf-8')


def generate_cybersource_sa_payload(order, redirect_url):
    """
    Generates a payload dict to send to CyberSource for Secure Acceptance

    Args:
        order (Order): An order
        redirect_url: (str): The URL to redirect to after order completion
    Returns:
        dict: the payload to send to CyberSource via Secure Acceptance
    """
    # http://apps.cybersource.com/library/documentation/dev_guides/Secure_Acceptance_WM/Secure_Acceptance_WM.pdf
    # Section: API Fields

    klass_key = None
    line = order.line_set.first()
    if line is not None:
        klass_key = line.klass_key
    klass = Klass.objects.get(klass_key=klass_key)

    # NOTE: be careful about max length here, many (all?) string fields have a max
    # length of 255. At the moment none of these fields should go over that, due to database
    # constraints or other reasons

    klass_title = remove_html_tags(klass.title)
    if not klass_title:
        raise ValidationError(
            'Klass {klass_key} title is either empty or contains only HTML.'.format(klass_key=klass_key)
        )

    bootcamp_title = remove_html_tags(klass.bootcamp.title)
    if not bootcamp_title:
        raise ValidationError(
            'Bootcamp {bootcamp_id} title is either empty or contains only HTML.'.format(bootcamp_id=klass.bootcamp.id)
        )

    payload = {
        'access_key': settings.CYBERSOURCE_ACCESS_KEY,
        'amount': str(order.total_price_paid),
        'consumer_id': get_social_username(order.user),
        'currency': 'USD',
        'locale': 'en-us',
        'item_0_code': 'klass',
        'item_0_name': '{}'.format(klass_title),
        'item_0_quantity': 1,
        'item_0_sku': '{}'.format(klass_key),
        'item_0_tax_amount': '0',
        'item_0_unit_price': str(order.total_price_paid),
        'line_item_count': 1,
        'override_custom_cancel_page': "{base}?status=cancel".format(base=redirect_url),
        'override_custom_receipt_page': "{base}?status=receipt&order={order}&award={award}".format(
            base=redirect_url,
            order=order.id,
            award=klass_key
        ),
        'reference_number': make_reference_id(order),
        'profile_id': settings.CYBERSOURCE_PROFILE_ID,
        'signed_date_time': datetime.now(tz=pytz.UTC).strftime(ISO_8601_FORMAT),
        'transaction_type': 'sale',
        'transaction_uuid': uuid.uuid4().hex,
        'unsigned_field_names': '',
        'merchant_defined_data1': 'bootcamp',
        'merchant_defined_data2': '{}'.format(bootcamp_title),
        'merchant_defined_data3': 'klass',
        'merchant_defined_data4': '{}'.format(klass_title),
        'merchant_defined_data5': '{}'.format(klass_key),
        'merchant_defined_data6': 'learner',
        'merchant_defined_data7': '{}'.format(order.user.profile.name),
        'merchant_defined_data8': '{}'.format(order.user.email),
    }

    field_names = sorted(list(payload.keys()) + ['signed_field_names'])
    payload['signed_field_names'] = ','.join(field_names)
    payload['signature'] = generate_cybersource_sa_signature(payload)

    return payload


def get_new_order_by_reference_number(reference_number):
    """
    Parse a reference number received from CyberSource and lookup the corresponding Order.

    Args:
        reference_number (str):
            A string which contains the order id and the instance which generated it
    Returns:
        Order:
            An order
    """
    if not reference_number.startswith(_REFERENCE_NUMBER_PREFIX):
        raise ParseException("Reference number must start with {}".format(_REFERENCE_NUMBER_PREFIX))
    reference_number = reference_number[len(_REFERENCE_NUMBER_PREFIX):]

    try:
        order_id_pos = reference_number.rindex('-')
    except ValueError:
        raise ParseException("Unable to find order number in reference number")

    try:
        order_id = int(reference_number[order_id_pos + 1:])
    except ValueError:
        raise ParseException("Unable to parse order number")

    prefix = reference_number[:order_id_pos]
    if prefix != settings.CYBERSOURCE_REFERENCE_PREFIX:
        log.error("CyberSource prefix doesn't match: %s != %s", prefix, settings.CYBERSOURCE_REFERENCE_PREFIX)
        raise ParseException("CyberSource prefix doesn't match")

    try:
        return Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise EcommerceException("Unable to find order {}".format(order_id))


def make_reference_id(order):
    """
    Make a reference id

    Args:
        order (Order):
            An order
    Returns:
        str:
            A reference number for use with CyberSource to keep track of orders
    """
    return "{}{}-{}".format(_REFERENCE_NUMBER_PREFIX, settings.CYBERSOURCE_REFERENCE_PREFIX, order.id)
