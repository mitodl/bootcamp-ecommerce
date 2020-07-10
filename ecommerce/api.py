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
from django.db.models import Q
from django_fsm import TransitionNotAllowed
import pytz
from rest_framework.exceptions import ValidationError

from applications.models import BootcampApplication
from applications.serializers import BootcampApplicationDetailSerializer
from ecommerce import tasks
from ecommerce.constants import CYBERSOURCE_DECISION_CANCEL
from ecommerce.exceptions import EcommerceException, ParseException
from ecommerce.models import Line, Order
from klasses.api import deactivate_run_enrollment
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.models import BootcampRun, BootcampRunEnrollment
from klasses.serializers import InstallmentSerializer
from mail.api import MailgunClient
from mail.v2 import api as mail_api
from mail.v2.constants import EMAIL_RECEIPT
from main.utils import remove_html_tags


ISO_8601_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
log = logging.getLogger(__name__)
_REFERENCE_NUMBER_PREFIX = "BOOTCAMP-"


@transaction.atomic
def create_unfulfilled_order(*, application, payment_amount):
    """
    Create a new Order which is not fulfilled for a bootcamp run.

    Args:
        application (BootcampApplication):
            A bootcamp application
        payment_amount (Decimal): The payment of the user
    Returns:
        Order: A newly created Order for the bootcamp run
    """
    payment_amount = Decimal(payment_amount)
    bootcamp_run = application.bootcamp_run
    run_key = bootcamp_run.run_key

    if payment_amount <= 0:
        raise ValidationError("Payment is less than or equal to zero")

    order = Order.objects.create(
        status=Order.CREATED,
        total_price_paid=payment_amount,
        user=application.user,
        application=application,
    )
    Line.objects.create(
        order=order,
        run_key=run_key,
        description="Installment for {}".format(bootcamp_run.title),
        price=payment_amount,
    )
    order.save_and_log(application.user)
    return order


@transaction.atomic
def create_refund_order(*, user, bootcamp_run, amount, application=None):
    """
    Create a refund order for a bootcamp run & user

    Args:
        user (User): The User receiving the refund
        bootcamp_run (BootcampRun): The BootcampRun to refund
        amount (Decimal): The amount to refund
        application (BootcampApplication): the application associated with the order

    Returns:
        Order: A newly created refund Order for the bootcamp run

    """
    refund_amount = -Decimal(amount)

    if refund_amount >= 0:
        raise EcommerceException("Amount to refund must be greater than zero")

    order = Order.objects.create(
        status=Order.FULFILLED,
        total_price_paid=refund_amount,
        user=user,
        application=application,
    )
    Line.objects.create(
        order=order,
        run_key=bootcamp_run.run_key,
        description="Refund for {}".format(bootcamp_run.title),
        price=refund_amount,
    )
    order.save_and_log(user)
    return order


@transaction.atomic
def process_refund(*, user, bootcamp_run, amount):
    """
    Deactivate an enrollment (if any), create a refund order, and update the application state

    Args:
        user (User): The user receiving the refund
        bootcamp_run (BootcampRun): The user's bootcamp run
        amount (Decimal): The amount to refund
    """
    application = BootcampApplication.objects.filter(
        user=user, bootcamp_run=bootcamp_run
    ).first()

    total_paid = Decimal(
        application.total_paid
        if application
        else sum(
            Order.objects.select_related("line")
            .filter(
                Q(user=user)
                & Q(line__run_key=bootcamp_run.run_key)
                & Q(status=Order.FULFILLED)
            )
            .values_list("total_price_paid", flat=True)
        )
    )

    if total_paid < amount:
        raise EcommerceException(f"Refund exceeds total payment of ${total_paid}")

    create_refund_order(
        user=user,
        bootcamp_run=bootcamp_run,
        amount=Decimal(amount),
        application=application,
    )
    enrollment = BootcampRunEnrollment.objects.filter(
        user=user, bootcamp_run=bootcamp_run
    ).first()
    if enrollment:
        deactivate_run_enrollment(
            enrollment, change_status=ENROLL_CHANGE_STATUS_REFUNDED
        )
    if application:
        application.refund()
        application.save()


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
    keys = payload["signed_field_names"].split(",")
    message = ",".join("{}={}".format(key, payload[key]) for key in keys)

    digest = hmac.new(
        settings.CYBERSOURCE_SECURITY_KEY.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    return b64encode(digest).decode("utf-8")


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

    run_key = None
    line = order.line_set.first()
    if line is not None:
        run_key = line.run_key
    bootcamp_run = BootcampRun.objects.get(run_key=run_key)

    # NOTE: be careful about max length here, many (all?) string fields have a max
    # length of 255. At the moment none of these fields should go over that, due to database
    # constraints or other reasons

    run_title = remove_html_tags(bootcamp_run.title)
    if not run_title:
        raise ValidationError(
            "Bootcamp run {run_key} title is either empty or contains only HTML.".format(
                run_key=run_key
            )
        )

    bootcamp_title = remove_html_tags(bootcamp_run.bootcamp.title)
    if not bootcamp_title:
        raise ValidationError(
            "Bootcamp {bootcamp_id} title is either empty or contains only HTML.".format(
                bootcamp_id=bootcamp_run.bootcamp.id
            )
        )

    payload = {
        "access_key": settings.CYBERSOURCE_ACCESS_KEY,
        "amount": str(order.total_price_paid),
        "currency": "USD",
        "locale": "en-us",
        "item_0_code": "klass",
        "item_0_name": "{}".format(run_title),
        "item_0_quantity": 1,
        "item_0_sku": "{}".format(run_key),
        "item_0_tax_amount": "0",
        "item_0_unit_price": str(order.total_price_paid),
        "line_item_count": 1,
        "override_custom_cancel_page": "{base}?status=cancel".format(base=redirect_url),
        "override_custom_receipt_page": "{base}?status=receipt&order={order}&award={award}".format(
            base=redirect_url, order=order.id, award=run_key
        ),
        "reference_number": make_reference_id(order),
        "profile_id": settings.CYBERSOURCE_PROFILE_ID,
        "signed_date_time": datetime.now(tz=pytz.UTC).strftime(ISO_8601_FORMAT),
        "transaction_type": "sale",
        "transaction_uuid": uuid.uuid4().hex,
        "unsigned_field_names": "",
        "merchant_defined_data1": "bootcamp",
        "merchant_defined_data2": "{}".format(bootcamp_title),
        "merchant_defined_data3": "klass",
        "merchant_defined_data4": "{}".format(run_title),
        "merchant_defined_data5": "{}".format(run_key),
        "merchant_defined_data6": "learner",
        "merchant_defined_data7": "{}".format(order.user.profile.name),
        "merchant_defined_data8": "{}".format(order.user.email),
    }

    field_names = sorted(list(payload.keys()) + ["signed_field_names"])
    payload["signed_field_names"] = ",".join(field_names)
    payload["signature"] = generate_cybersource_sa_signature(payload)

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
        raise ParseException(
            "Reference number must start with {}".format(_REFERENCE_NUMBER_PREFIX)
        )
    reference_number = reference_number[len(_REFERENCE_NUMBER_PREFIX) :]

    try:
        order_id_pos = reference_number.rindex("-")
    except ValueError:
        raise ParseException("Unable to find order number in reference number")

    try:
        order_id = int(reference_number[order_id_pos + 1 :])
    except ValueError:
        raise ParseException("Unable to parse order number")

    prefix = reference_number[:order_id_pos]
    if prefix != settings.CYBERSOURCE_REFERENCE_PREFIX:
        log.error(
            "CyberSource prefix doesn't match: %s != %s",
            prefix,
            settings.CYBERSOURCE_REFERENCE_PREFIX,
        )
        raise ParseException("CyberSource prefix doesn't match")

    try:
        return Order.objects.select_related("application").get(id=order_id)
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
    return "{}{}-{}".format(
        _REFERENCE_NUMBER_PREFIX, settings.CYBERSOURCE_REFERENCE_PREFIX, order.id
    )


def complete_successful_order(order):
    """
    Once an order is fulfilled, we need to create an enrollment and notify other services.

    Args:
        order (Order): An order which has just been fulfilled
    """
    order.status = Order.FULFILLED
    order.save_and_log(None)

    run = order.get_bootcamp_run()
    application = order.application
    if application.is_paid_in_full:
        BootcampRunEnrollment.objects.update_or_create(
            user=order.user,
            bootcamp_run=run,
            defaults={"active": True, "change_status": None},
        )

        try:
            application.complete()
            application.save()
        except TransitionNotAllowed:
            log.exception(
                "Application received full payment but state cannot transition to COMPLETE from %s for order %d",
                application.state,
                order.id,
            )

    tasks.send_receipt_email.delay(application.id)


def handle_rejected_order(*, order, decision):
    """
    Report a response from Cybersource with a failed response of some kind

    Args:
        order (Order): An order
        decision (str): The decision from Cybersource's response
    """
    order.status = Order.FAILED
    order.save_and_log(None)

    log.warning(
        "Order fulfillment failed: received a decision that wasn't ACCEPT for order %s",
        order,
    )
    if decision != CYBERSOURCE_DECISION_CANCEL:
        try:
            MailgunClient().send_individual_email(
                "Order fulfillment failed, decision={decision}".format(
                    decision=decision
                ),
                "Order fulfillment failed for order {order}".format(order=order),
                settings.ECOMMERCE_EMAIL,
            )
        except:  # pylint: disable=bare-except
            log.exception(
                "Error occurred when sending the email to notify "
                "about order fulfillment failure for order %s",
                order,
            )


def serialize_user_bootcamp_runs(user):
    """
    Returns serialized bootcamp run and payment details for a user.

    Args:
        user (User): a user

    Returns:
        list: list of dictionaries describing a bootcamp run and payments for it by the user
    """
    return [
        serialize_user_bootcamp_run(user, bootcamp_run)
        for bootcamp_run in BootcampRun.objects.filter(applications__user=user)
        .select_related("bootcamp")
        .order_by("run_key")
    ]


def serialize_user_bootcamp_run(user, bootcamp_run):
    """
    Returns the bootcamp run info for the user with payments details.

    Args:
        user (User): a user
        bootcamp_run (klasses.models.BootcampRun): a bootcamp run

    Returns:
        dict: a dictionary describing a bootcamp run and payments for it by the user
    """

    from ecommerce.serializers import LineSerializer

    return {
        "run_key": bootcamp_run.run_key,
        "bootcamp_run_name": bootcamp_run.title,
        "display_title": bootcamp_run.display_title,
        "start_date": bootcamp_run.start_date,
        "end_date": bootcamp_run.end_date,
        "price": bootcamp_run.personal_price(user),
        "total_paid": Line.total_paid_for_bootcamp_run(user, bootcamp_run.run_key).get(
            "total"
        )
        or Decimal("0.00"),
        "payments": LineSerializer(
            Line.for_user_bootcamp_run(user, bootcamp_run.run_key), many=True
        ).data,
        "installments": InstallmentSerializer(
            bootcamp_run.installment_set.order_by("deadline"), many=True
        ).data,
    }


def send_receipt_email(application_id):
    """
    Send a receipt email

    Args:
        application_id(str): the application id to send an email for
    """
    # NOTE: this receipt email includes a whole payment history so it'd more of a snapshot
    try:
        application = BootcampApplication.objects.prefetch_state_data().get(
            id=application_id
        )
    except BootcampApplication.DoesNotExist:
        log.exception(
            "Tried to send receipt email for application id=%s, but it doesn't exist",
            application_id,
        )
        return

    if not application.orders.exists():
        log.error(
            "Tried to send receipt email for application with id=%s, but it has no fulfilled orders",
            application_id,
        )
        return

    extra_context = {
        "application": BootcampApplicationDetailSerializer(instance=application).data
    }

    mail_api.send_message(
        mail_api.message_for_recipient(
            application.user.email,
            mail_api.context_for_user(extra_context=extra_context),
            EMAIL_RECEIPT,
        )
    )
