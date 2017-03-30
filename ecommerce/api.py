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
from ecommerce.exceptions import (
    EcommerceException,
    ParseException,
)
from ecommerce.models import (
    Line,
    Order,
)
from klasses.models import Klass


ISO_8601_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
log = logging.getLogger(__name__)
_REFERENCE_NUMBER_PREFIX = 'BOOTCAMP-'


def get_total_paid(user, klass_id):
    """
    Get total paid for a klass for a user
    Args:
        user (User):
            The purchaser of the klass
        klass_id (int):
            A klass id, a class within a bootcamp

    Returns:
        Decimal: The total amount paid by a user for a klass
    """
    return Line.objects.filter(
        order__status=Order.FULFILLED,
        order__user=user,
        klass_id=klass_id,
    ).aggregate(price=Sum('price'))['price'] or Decimal(0)


@transaction.atomic
def create_unfulfilled_order(user, klass_id, total):
    """
    Create a new Order which is not fulfilled for a klass.

    Args:
        user (User):
            The purchaser of the klass
        klass_id (int):
            A klass id, a class within a bootcamp
        total (Decimal): The payment of the user
    Returns:
        Order: A newly created Order for the klass
    """
    total = Decimal(total)
    try:
        klass = Klass.objects.get(klass_id=klass_id)
    except Klass.DoesNotExist:
        # In the near future we should do other checking here based on information from Bootcamp REST API
        raise ValidationError("Incorrect klass id {}".format(klass_id))
    if total <= 0:
        raise ValidationError("Payment is less than or equal to zero")

    already_paid = get_total_paid(user, klass_id)
    if total + already_paid > klass.price:
        raise ValidationError(
            "Payment of ${total} plus already paid ${already_paid} for {klass} would be"
            " greater than total price of ${klass_price}".format(
                total=total,
                klass=klass.title,
                already_paid=already_paid,
                klass_price=klass.price,
            )
        )

    order = Order.objects.create(
        status=Order.CREATED,
        total_price_paid=total,
        user=user,
    )
    Line.objects.create(
        order=order,
        klass_id=klass_id,
        description='Installment for {}'.format(klass.title),
        price=total,
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

    klass_id = None
    line = order.line_set.first()
    if line is not None:
        klass_id = line.klass_id
    klass = Klass.objects.get(klass_id=klass_id)

    # NOTE: be careful about max length here, many (all?) string fields have a max
    # length of 255. At the moment none of these fields should go over that, due to database
    # constraints or other reasons

    payload = {
        'access_key': settings.CYBERSOURCE_ACCESS_KEY,
        'amount': str(order.total_price_paid),
        'consumer_id': get_social_username(order.user),
        'currency': 'USD',
        'locale': 'en-us',
        'item_0_code': 'klass',
        'item_0_name': '{}'.format(klass.title),
        'item_0_quantity': 1,
        'item_0_sku': '{}'.format(klass_id),
        'item_0_tax_amount': '0',
        'item_0_unit_price': str(order.total_price_paid),
        'line_item_count': 1,
        'override_custom_cancel_page': "{}?status=cancel".format(redirect_url),
        'override_custom_receipt_page': "{}?status=receipt".format(redirect_url),
        'reference_number': make_reference_id(order),
        'profile_id': settings.CYBERSOURCE_PROFILE_ID,
        'signed_date_time': datetime.now(tz=pytz.UTC).strftime(ISO_8601_FORMAT),
        'transaction_type': 'sale',
        'transaction_uuid': uuid.uuid4().hex,
        'unsigned_field_names': '',
        'merchant_defined_data1': 'klass',
        'merchant_defined_data2': '{}'.format(klass.title),
        'merchant_defined_data3': '{}'.format(klass_id),
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
