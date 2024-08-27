"""
Test for ecommerce functions
"""

import hashlib
import hmac
from base64 import b64encode
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
import pytz
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.management.base import CommandError
from mitol.common.pytest_utils import any_instance_of
from rest_framework.exceptions import ValidationError

from applications.constants import AppStates
from applications.factories import BootcampApplicationFactory
from applications.models import BootcampApplication
from ecommerce.api import (
    ISO_8601_FORMAT,
    WireTransfer,
    complete_successful_order,
    create_refund_order,
    generate_cybersource_sa_payload,
    generate_cybersource_sa_signature,
    get_new_order_by_reference_number,
    import_wire_transfer,
    import_wire_transfers,
    make_reference_id,
    parse_wire_transfer_csv,
    process_refund,
    send_receipt_email,
    serialize_user_bootcamp_run,
    serialize_user_bootcamp_runs,
)
from ecommerce.exceptions import (
    EcommerceException,
    ParseException,
    WireTransferImportException,
)
from ecommerce.factories import LineFactory, OrderFactory
from ecommerce.models import Line, Order, WireTransferReceipt
from ecommerce.serializers import LineSerializer
from ecommerce.test_utils import create_test_application, create_test_order
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.factories import (
    BootcampRunEnrollmentFactory,
    BootcampRunFactory,
    InstallmentFactory,
)
from klasses.models import BootcampRun, BootcampRunEnrollment
from klasses.serializers import InstallmentSerializer
from profiles.factories import ProfileFactory

pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def application():
    """An application for testing"""
    yield create_test_application()


@pytest.fixture
def user(application):
    """A user with social auth"""
    yield application.user


@pytest.fixture
def bootcamp_run(application):
    """
    Creates a purchasable bootcamp run. Bootcamp run price is at least $200, in two installments
    """
    yield application.bootcamp_run


@pytest.fixture
def paid_order_elements():
    """
    Sets up a scenario where a fully-paid order has been created for a bootcamp application
    """
    installment = InstallmentFactory.create()
    application = BootcampApplicationFactory.create(
        bootcamp_run=installment.bootcamp_run, state=AppStates.AWAITING_PAYMENT
    )
    order = OrderFactory.create(
        status=Order.CREATED,
        total_price_paid=installment.amount,
        application=application,
        user=application.user,
    )
    line = LineFactory.create(
        order=order, price=installment.amount, bootcamp_run=application.bootcamp_run
    )
    return SimpleNamespace(
        order=order,
        line=line,
        run=installment.bootcamp_run,
        application=application,
        user=application.user,
    )


@pytest.fixture()
def patched_novoed_tasks(mocker):
    """Patched novoed-related tasks"""
    return mocker.patch("klasses.api.novoed_tasks")


@pytest.mark.parametrize("payment_amount", [0, -1.23])
def test_less_or_equal_to_zero(application, payment_amount):
    """
    An order may not have a negative or zero price
    """
    with pytest.raises(ValidationError) as ex:
        create_test_order(application, payment_amount, fulfilled=False)

    assert ex.value.args[0] == "Payment is less than or equal to zero"


CYBERSOURCE_ACCESS_KEY = "access"
CYBERSOURCE_PROFILE_ID = "profile"
CYBERSOURCE_SECURITY_KEY = "security"
CYBERSOURCE_REFERENCE_PREFIX = "prefix"


@pytest.fixture(autouse=True)
def cybersource_settings(settings):
    """
    Set some Cybersource settings
    """
    settings.CYBERSOURCE_ACCESS_KEY = CYBERSOURCE_ACCESS_KEY
    settings.CYBERSOURCE_PROFILE_ID = CYBERSOURCE_PROFILE_ID
    settings.CYBERSOURCE_SECURITY_KEY = CYBERSOURCE_SECURITY_KEY
    settings.CYBERSOURCE_REFERENCE_PREFIX = CYBERSOURCE_REFERENCE_PREFIX


def test_valid_signature():
    """
    Signature is made up of a ordered key value list signed using HMAC 256 with a security key
    """
    payload = {"x": "y", "abc": "def", "key": "value", "signed_field_names": "abc,x"}
    signature = generate_cybersource_sa_signature(payload)

    message = ",".join("{}={}".format(key, payload[key]) for key in ["abc", "x"])

    digest = hmac.new(
        CYBERSOURCE_SECURITY_KEY.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    assert b64encode(digest).decode("utf-8") == signature


@pytest.mark.parametrize("user_ip", ["194.100.0.1", "", None])
def test_signed_payload(mocker, application, bootcamp_run, user_ip):
    """
    A valid payload should be signed appropriately
    """
    payment = 123.45
    order = create_test_order(application, payment, fulfilled=False)
    transaction_uuid = "hex"

    now = datetime.now(tz=pytz.UTC)
    now_mock = mocker.MagicMock(return_value=now)

    mocker.patch("ecommerce.api.datetime", autospec=True, now=now_mock)
    mocker.patch(
        "ecommerce.api.uuid.uuid4",
        autospec=True,
        return_value=mocker.MagicMock(hex=transaction_uuid),
    )

    payload = generate_cybersource_sa_payload(
        order, "dashboard_url", ip_address=user_ip
    )
    signature = payload.pop("signature")
    assert generate_cybersource_sa_signature(payload) == signature
    signed_field_names = payload["signed_field_names"].split(",")
    assert signed_field_names == sorted(payload.keys())

    expected_payload = {
        "access_key": CYBERSOURCE_ACCESS_KEY,
        "amount": str(order.total_price_paid),
        "currency": "USD",
        "item_0_code": "klass",
        "item_0_name": "{}".format(bootcamp_run.title),
        "item_0_quantity": 1,
        "item_0_sku": "{}".format(bootcamp_run.run_key),
        "item_0_tax_amount": "0",
        "item_0_unit_price": str(order.total_price_paid),
        "line_item_count": 1,
        "locale": "en-us",
        "override_custom_cancel_page": "dashboard_url?status=cancel",
        "override_custom_receipt_page": "dashboard_url?status=receipt&order={}&award={}".format(
            order.id, bootcamp_run.run_key
        ),
        "reference_number": make_reference_id(order),
        "profile_id": CYBERSOURCE_PROFILE_ID,
        "signed_date_time": now.strftime(ISO_8601_FORMAT),
        "signed_field_names": ",".join(signed_field_names),
        "transaction_type": "sale",
        "transaction_uuid": transaction_uuid,
        "unsigned_field_names": "",
        "merchant_defined_data1": "bootcamp",
        "merchant_defined_data2": "{}".format(bootcamp_run.bootcamp.title),
        "merchant_defined_data3": "klass",
        "merchant_defined_data4": "{}".format(bootcamp_run.title),
        "merchant_defined_data5": "{}".format(bootcamp_run.run_key),
        "merchant_defined_data6": "learner",
        "merchant_defined_data7": "{}".format(order.user.profile.name),
        "merchant_defined_data8": "{}".format(order.user.email),
    }
    if user_ip:
        expected_payload["customer_ip_address"] = user_ip
    assert payload == expected_payload
    now_mock.assert_called_with(tz=pytz.UTC)


@pytest.mark.parametrize("invalid_title", ["", "<h1></h1>"])
def test_with_empty_or_html_run_title(application, bootcamp_run, invalid_title):
    """Verify that Validation error raises if title of bootcamp run has only HTML or empty."""
    bootcamp_run.title = invalid_title
    bootcamp_run.save()
    order = create_test_order(application, "123.45", fulfilled=False)
    with pytest.raises(ValidationError) as ex:
        generate_cybersource_sa_payload(order, "dashboard_url")

    assert ex.value.args[
        0
    ] == "Bootcamp run {run_key} title is either empty or contains only HTML.".format(
        run_key=bootcamp_run.run_key
    )


@pytest.mark.parametrize("invalid_title", ["", "<h1></h1>"])
def test_with_empty_or_html_bootcamp_title(application, bootcamp_run, invalid_title):
    """Verify that Validation error raises if title of bootcamp has only HTML or empty."""
    bootcamp_run.bootcamp.title = invalid_title
    bootcamp_run.bootcamp.save()
    order = create_test_order(application, "123.45", fulfilled=False)
    with pytest.raises(ValidationError) as ex:
        generate_cybersource_sa_payload(order, "dashboard_url")

    assert ex.value.args[
        0
    ] == "Bootcamp {bootcamp_id} title is either empty or contains only HTML.".format(
        bootcamp_id=bootcamp_run.bootcamp.id
    )


def test_make_reference_id(application):
    """
    make_reference_id should concatenate the reference prefix and the order id
    """
    order = create_test_order(application, 123, fulfilled=False)
    assert "BOOTCAMP-{}-{}".format(
        CYBERSOURCE_REFERENCE_PREFIX, order.id
    ) == make_reference_id(order)


def test_get_new_order_by_reference_number(application):
    """
    get_new_order_by_reference_number returns an Order with status created
    """
    order = create_test_order(application, 123, fulfilled=False)
    same_order = get_new_order_by_reference_number(make_reference_id(order))
    assert same_order.id == order.id


@pytest.mark.parametrize(
    "reference_number, exception_message",
    [
        ("XYZ-1-3", "Reference number must start with BOOTCAMP-"),
        ("BOOTCAMP-no_dashes_here", "Unable to find order number in reference number"),
        ("BOOTCAMP-something-NaN", "Unable to parse order number"),
        ("BOOTCAMP-not_matching-3", "CyberSource prefix doesn't match"),
    ],
)
def test_parse(reference_number, exception_message):
    """
    Test parse errors are handled well
    """
    with pytest.raises(ParseException) as ex:
        get_new_order_by_reference_number(reference_number)
    assert ex.value.args[0] == exception_message


def test_status(application):
    """
    get_order_by_reference_number should only get orders with status=CREATED
    """
    order = create_test_order(application, 123, fulfilled=False)
    order.status = Order.FAILED
    order.save()

    with pytest.raises(EcommerceException) as ex:
        # change order number to something not likely to already exist in database
        order.id = 98_765_432
        assert not Order.objects.filter(id=order.id).exists()
        get_new_order_by_reference_number(make_reference_id(order))
    assert ex.value.args[0] == "Unable to find order {}".format(order.id)


@pytest.fixture()
def test_data():
    """
    Sets up the data for all the tests in this module
    """
    profile = ProfileFactory.create()
    run_paid = BootcampRunFactory.create()
    BootcampApplicationFactory.create(
        bootcamp_run=run_paid, user=profile.user, state=AppStates.AWAITING_PAYMENT.value
    )
    run_not_paid = BootcampRunFactory.create()
    BootcampApplicationFactory.create(
        bootcamp_run=run_not_paid,
        user=profile.user,
        state=AppStates.AWAITING_PAYMENT.value,
    )

    InstallmentFactory.create(bootcamp_run=run_paid)
    InstallmentFactory.create(bootcamp_run=run_not_paid)

    order = OrderFactory.create(user=profile.user, status=Order.FULFILLED)
    LineFactory.create(order=order, bootcamp_run=run_paid, price=627.34)

    return profile.user, run_paid, run_not_paid


def test_serialize_user_run_paid(test_data):
    """
    Test for serialize_user_bootcamp_run for a paid bootcamp run
    """
    user, run_paid, _ = test_data

    expected_ret = {
        "run_key": run_paid.run_key,
        "bootcamp_run_name": run_paid.title,
        "display_title": run_paid.display_title,
        "start_date": run_paid.start_date,
        "end_date": run_paid.end_date,
        "price": run_paid.personal_price(user),
        "total_paid": Decimal("627.34"),
        "payments": LineSerializer(
            Line.for_user_bootcamp_run(user, run_paid), many=True
        ).data,
        "installments": InstallmentSerializer(
            run_paid.installment_set.order_by("deadline"), many=True
        ).data,
    }
    assert expected_ret == serialize_user_bootcamp_run(user, run_paid)


def test_serialize_user_run_not_paid(test_data):
    """
    Test for serialize_user_bootcamp_run for a not paid bootcamp run
    """
    user, _, run_not_paid = test_data

    expected_ret = {
        "run_key": run_not_paid.run_key,
        "bootcamp_run_name": run_not_paid.title,
        "display_title": run_not_paid.display_title,
        "start_date": run_not_paid.start_date,
        "end_date": run_not_paid.end_date,
        "price": run_not_paid.personal_price(user),
        "total_paid": Decimal("0.00"),
        "payments": [],
        "installments": InstallmentSerializer(
            run_not_paid.installment_set.order_by("deadline"), many=True
        ).data,
    }
    assert expected_ret == serialize_user_bootcamp_run(user, run_not_paid)


def test_serialize_user_bootcamp_runs(test_data):
    """
    Test for serialize_user_bootcamp_runs in normal case
    """
    user, run_paid, run_not_paid = test_data
    expected_ret = [
        {
            "run_key": run_paid.run_key,
            "bootcamp_run_name": run_paid.title,
            "display_title": run_paid.display_title,
            "start_date": run_paid.start_date,
            "end_date": run_paid.end_date,
            "price": run_paid.price,
            "total_paid": Decimal("627.34"),
            "payments": LineSerializer(
                Line.for_user_bootcamp_run(user, run_paid), many=True
            ).data,
            "installments": InstallmentSerializer(
                run_paid.installment_set.order_by("deadline"), many=True
            ).data,
        },
        {
            "run_key": run_not_paid.run_key,
            "bootcamp_run_name": run_not_paid.title,
            "display_title": run_not_paid.display_title,
            "start_date": run_not_paid.start_date,
            "end_date": run_not_paid.end_date,
            "price": run_not_paid.price,
            "total_paid": Decimal("0.00"),
            "payments": [],
            "installments": InstallmentSerializer(
                run_not_paid.installment_set.order_by("deadline"), many=True
            ).data,
        },
    ]
    assert sorted(
        expected_ret, key=lambda x: x["run_key"]
    ) == serialize_user_bootcamp_runs(user)


def test_send_verify_email_change_email(mocker, user):
    """Test send_receipt_email sends a receipt email"""
    application = BootcampApplicationFactory.create()
    OrderFactory.create(
        application=application, user=application.user, status=Order.FULFILLED
    )

    send_messages_mock = mocker.patch("mail.v2.api.send_messages")

    send_receipt_email(application.id)

    send_messages_mock.assert_called_once_with([any_instance_of(EmailMessage)])

    email = send_messages_mock.call_args[0][0][0]
    assert application.bootcamp_run.title in email.body


@pytest.mark.parametrize("has_enrollment", [True, False])
@pytest.mark.parametrize("has_application", [True, False])
def test_refund_enrollment(patched_novoed_tasks, has_enrollment, has_application, user):
    """
    Test that deactivate_run_enrollment creates a refund order and
    updates enrollment and application objects
    """
    bootcamp_run = BootcampRunFactory.create(novoed_course_stub=None)
    if has_enrollment:
        BootcampRunEnrollmentFactory.create(bootcamp_run=bootcamp_run, user=user)
    application = (
        BootcampApplicationFactory.create(
            user=user, bootcamp_run=bootcamp_run, state=AppStates.COMPLETE
        )
        if has_application
        else None
    )
    refund_amount = 1.50
    LineFactory.create(
        price=3,
        bootcamp_run=bootcamp_run,
        order=OrderFactory(
            user=user,
            application=application,
            status=Order.FULFILLED,
            total_price_paid=3,
        ),
    )
    process_refund(user=user, bootcamp_run=bootcamp_run, amount=refund_amount)
    enrollment = BootcampRunEnrollment.objects.filter(
        user=user, bootcamp_run=bootcamp_run
    ).first()
    if has_enrollment:
        assert enrollment is not None
        assert enrollment.active is False
        assert enrollment.change_status == ENROLL_CHANGE_STATUS_REFUNDED
    else:
        assert enrollment is None
    order = Order.objects.get(
        total_price_paid=-refund_amount, application=application, user=user
    )
    assert order.status == Order.FULFILLED
    assert Line.objects.filter(
        order=order,
        price=-refund_amount,
        description="Refund for {}".format(bootcamp_run.title),
    ).exists()
    if has_application:
        assert (
            BootcampApplication.objects.get(id=application.id).state
            == AppStates.REFUNDED.value
        )


@pytest.mark.parametrize("has_application", [True, False])
def test_refund_exceeds_payment(has_application, user):
    """
    Test that refunded amount cannot exceed total paid
    """
    bootcamp_run = BootcampRunFactory.create()
    application = (
        BootcampApplicationFactory.create(
            user=user, bootcamp_run=bootcamp_run, state=AppStates.COMPLETE
        )
        if has_application
        else None
    )
    # Create 3 orders totalling $30 in payments
    orders = OrderFactory.create_batch(
        3,
        user=user,
        application=application,
        status=Order.FULFILLED,
        total_price_paid=10,
    )
    for order in orders:
        LineFactory.create(price=10, bootcamp_run=bootcamp_run, order=order)

    with pytest.raises(EcommerceException) as exc:
        process_refund(user=user, bootcamp_run=bootcamp_run, amount=45.50)
    assert exc.value.args[0] == "Refund exceeds total payment of $30.00"
    process_refund(user=user, bootcamp_run=bootcamp_run, amount=11)
    process_refund(user=user, bootcamp_run=bootcamp_run, amount=11)
    with pytest.raises(EcommerceException) as exc:
        process_refund(user=user, bootcamp_run=bootcamp_run, amount=11)
    assert exc.value.args[0] == "Refund exceeds total payment of $8.00"


@pytest.mark.parametrize("amount", [-5, 0])
def test_bad_refund_amount(amount):
    """Test that an invalid refund amount raises an exception"""
    enrollment = BootcampRunEnrollmentFactory.create()
    with pytest.raises(EcommerceException) as exc:
        create_refund_order(
            user=enrollment.user, bootcamp_run=enrollment.bootcamp_run, amount=amount
        )
    assert exc.value.args[0] == "Amount to refund must be greater than zero"


@pytest.mark.parametrize("enrollment_exists", [True, False])
def test_complete_successful_order(paid_order_elements, enrollment_exists):
    """Test that enrollment, application values updated correctly on successful order"""
    if enrollment_exists:
        BootcampRunEnrollmentFactory.create(
            user=paid_order_elements.user,
            bootcamp_run=paid_order_elements.run,
            active=False,
            change_status=ENROLL_CHANGE_STATUS_REFUNDED,
        )
    complete_successful_order(paid_order_elements.order)
    assert (
        BootcampApplication.objects.filter(
            id=paid_order_elements.application.id, state=AppStates.COMPLETE.value
        ).exists()
        is True
    )
    enrollment = BootcampRunEnrollment.objects.get(
        user=paid_order_elements.user, bootcamp_run=paid_order_elements.run
    )
    assert enrollment.active is True
    assert enrollment.change_status is None


@pytest.mark.parametrize(
    "feature_flag,has_stub",
    [[True, True], [True, False], [False, True], [False, False]],
)
def test_complete_successful_order_novoed(
    mocker, settings, paid_order_elements, feature_flag, has_stub
):
    """
    complete_successful_order should call a task that enrolls the given user in a NovoEd course
    """
    patched_novoed_tasks = mocker.patch("klasses.api.novoed_tasks")
    settings.FEATURES["NOVOED_INTEGRATION"] = feature_flag
    if not has_stub:
        paid_order_elements.run.novoed_course_stub = None
        paid_order_elements.run.save()
    complete_successful_order(paid_order_elements.order)
    if feature_flag and has_stub:
        patched_novoed_tasks.enroll_users_in_novoed_course.delay.assert_called_once_with(
            user_ids=[paid_order_elements.user.id],
            novoed_course_stub=paid_order_elements.run.novoed_course_stub,
        )
    else:
        patched_novoed_tasks.enroll_users_in_novoed_course.delay.assert_not_called()


@pytest.mark.parametrize(
    "feature_flag,has_stub",
    [[True, True], [True, False], [False, True], [False, False]],
)
def test_refund_novoed(
    settings, paid_order_elements, patched_novoed_tasks, feature_flag, has_stub
):
    """
    process_refund should call a task that unenrolls the user from a NovoEd course
    """
    settings.FEATURES["NOVOED_INTEGRATION"] = feature_flag
    if not has_stub:
        paid_order_elements.run.novoed_course_stub = None
        paid_order_elements.run.save()
    paid_order_elements.order.status = Order.FULFILLED
    paid_order_elements.order.save()
    BootcampRunEnrollmentFactory.create(
        user=paid_order_elements.user, bootcamp_run=paid_order_elements.run
    )
    process_refund(
        user=paid_order_elements.user,
        bootcamp_run=paid_order_elements.run,
        amount=paid_order_elements.line.price,
    )
    if feature_flag and has_stub:
        patched_novoed_tasks.unenroll_user_from_novoed_course.delay.assert_called_once_with(
            user_id=paid_order_elements.user.id,
            novoed_course_stub=paid_order_elements.run.novoed_course_stub,
        )
    else:
        patched_novoed_tasks.unenroll_user_from_novoed_course.delay.assert_not_called()


def test_parse_wire_transfer_csv():
    """parse_wire_transfer_csv should convert CSV input to WireTransfer objects"""
    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)
    assert header_row == [
        "Id",
        "Date transfers requested ",
        "Learner Email",
        "Zendesk Ticket",
        "Bootcamp ID",
        "Payor Name",
        "Learner email",
        "Payment Date",
        "Bootcamp Name",
        "Bootcamp Start Date",
        "Bootcamp Run ID",
        "Amount",
        "Transfer Type",
        "SAP doc # - Cash Application",
        "Order Updated By",
        "Refund Order ID",
        "Order Completed Date",
        "Errors",
        "Ignore?",
    ]
    assert wire_transfers == [
        WireTransfer(
            id=2,
            learner_email="hdoof@odl.mit.edu",
            amount=Decimal(100),
            bootcamp_start_date=datetime(2019, 12, 21),  # noqa: DTZ001
            bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
            bootcamp_name="How to be Evil",
            row=[
                "2",
                "11/1/1973",
                "hdoof@odl.mit.edu",
                "",
                "1",
                "Heinz Doofenschmirtz",
                "hdoof@odl.mit.edu",
                "Oct 20, 2019",
                "How to be Evil",
                "Dec 21, 2019",
                "bootcamp-v1:public+SVCR-ol+R1",
                "100",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ),
        WireTransfer(
            id=3,
            learner_email="pplatypus@odl.mit.edu",
            amount=Decimal(50),
            bootcamp_start_date=datetime(2019, 12, 21),  # noqa: DTZ001
            bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
            bootcamp_name="How to be Evil",
            row=[
                "3",
                "11/1/1944",
                "pplatypus@odl.mit.edu",
                "",
                "1",
                "Perry the Platypus",
                "pplatypus@odl.mit.edu",
                "Oct 20, 2019",
                "How to be Evil",
                "Dec 21, 2019",
                "bootcamp-v1:public+SVCR-ol+R1",
                "50",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ],
        ),
    ]


def test_parse_wire_transfer_csv_no_header(tmp_path):
    """parse_wire_transfer_csv should error if no header is found"""
    path = tmp_path / "test.csv"
    open(path, "w")  # create file  # noqa: PTH123, SIM115
    with pytest.raises(WireTransferImportException) as ex:
        parse_wire_transfer_csv(path)

    assert ex.value.args[0] == "Unable to find header row"


def test_parse_wire_transfer_csv_missing_header(tmp_path):
    """parse_wire_transfer_csv should error if not all fields are present"""
    path = tmp_path / "test.csv"
    with open(path, "w") as f:  # noqa: PTH123
        f.write("Learner Email,Id\n")
        f.write("hdoof@odl.mit.edu,20\n")

    with pytest.raises(WireTransferImportException) as ex:
        parse_wire_transfer_csv(path)

    assert ex.value.args[0] == "Unable to find column header Amount"


@pytest.mark.parametrize("paid_in_full", [True, False])
def test_import_wire_transfer(mocker, paid_in_full):
    """import_wire_transfer should store a wire transfer in the database and create an order for it"""
    mock_hubspot_sync = mocker.patch("ecommerce.api.sync_hubspot_application")
    user = User.objects.create(email="hdoof@odl.mit.edu")
    price = 100
    run = BootcampRunFactory.create(bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1")
    InstallmentFactory.create(bootcamp_run=run, amount=price)
    application = BootcampApplicationFactory.create(
        bootcamp_run=run, user=user, state=AppStates.AWAITING_PAYMENT.value
    )

    wire_transfer = WireTransfer(
        id=2,
        learner_email=user.email,
        amount=Decimal(price if paid_in_full else price / 2),
        bootcamp_start_date=run.start_date,
        bootcamp_name=run.bootcamp.title,
        bootcamp_run_id=run.bootcamp_run_id,
        row=[],
    )
    import_wire_transfer(wire_transfer, [])
    receipt = WireTransferReceipt.objects.get(wire_transfer_id=wire_transfer.id)
    assert receipt.data == {}
    order = receipt.order
    assert order.status == Order.FULFILLED
    assert order.total_price_paid == wire_transfer.amount
    assert order.application == application
    assert order.user == user
    assert order.payment_type == Order.WIRE_TRANSFER_TYPE
    line = order.line_set.get()
    assert line.price == wire_transfer.amount
    assert line.bootcamp_run == run
    assert order.orderaudit_set.count() == 1

    # function should handle importing twice by skipping the second import attempt
    import_wire_transfer(wire_transfer, [])
    assert WireTransferReceipt.objects.count() == 1
    assert Order.objects.count() == 1
    assert Line.objects.count() == 1
    application.refresh_from_db()
    assert application.state == (
        AppStates.COMPLETE.value if paid_in_full else AppStates.AWAITING_PAYMENT.value
    )
    assert mock_hubspot_sync.call_count == (0 if paid_in_full else 1)


def test_import_wire_transfer_missing_user():
    """import_wire_transfer should error if a user does not exist"""
    wire_transfer = WireTransfer(
        id=2,
        learner_email="hdoof@odl.mit.edu",
        amount=Decimal(100),
        bootcamp_start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_name="How to be Evil",
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
        row=[],
    )
    with pytest.raises(User.DoesNotExist):
        import_wire_transfer(wire_transfer, [])


def test_import_wire_transfers_missing_run():
    """import_wire_transfer should error if a run doesn't match up with anything in the database"""
    doof_email = "hdoof@odl.mit.edu"
    User.objects.create(email=doof_email)
    wire_transfer = WireTransfer(
        id=2,
        learner_email=doof_email,
        amount=Decimal(100),
        bootcamp_start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_name="How to be Evil",
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
        row=[],
    )
    with pytest.raises(BootcampRun.DoesNotExist):
        import_wire_transfer(wire_transfer, [])


def test_import_wire_transfers_no_matching_run_id():
    """import_wire_transfer should error if the given bootcamp run id doesn't match any run"""
    doof_email = "hdoof@odl.mit.edu"
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    User.objects.create(email=doof_email)
    wire_transfer = WireTransfer(
        id=2,
        learner_email=doof_email,
        amount=Decimal(100),
        bootcamp_start_date=run.start_date,
        bootcamp_name=run.bootcamp.title,
        bootcamp_run_id="bootcamp-v1:public+HTBG-ol+R1",
        row=[...],
    )
    with pytest.raises(BootcampRun.DoesNotExist):
        import_wire_transfer(wire_transfer, [])


def test_import_wire_transfers_missing_application():
    """import_wire_transfer should error if a user hasn't created an application yet"""
    doof_email = "hdoof@odl.mit.edu"
    User.objects.create(email=doof_email)
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    wire_transfer = WireTransfer(
        id=2,
        learner_email=doof_email,
        amount=Decimal(100),
        bootcamp_start_date=run.start_date,
        bootcamp_run_id=run.bootcamp_run_id,
        bootcamp_name=run.bootcamp.title,
        row=[],
    )
    with pytest.raises(BootcampApplication.DoesNotExist):
        import_wire_transfer(wire_transfer, [])


def test_import_wire_transfers_update_receipt(mocker):
    """Check for update receipt"""
    mocker.patch("ecommerce.api.tasks.send_receipt_email")
    doof_email = "hdoof@odl.mit.edu"
    user = User.objects.create(email=doof_email)
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    BootcampApplicationFactory.create(
        bootcamp_run=run, user=user, state=AppStates.AWAITING_PAYMENT.value
    )

    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)
    import_wire_transfer(wire_transfers[0], header_row, False)  # noqa: FBT003
    receipt = WireTransferReceipt.objects.get(wire_transfer_id=2)
    assert receipt.data["SAP doc # - Cash Application"] == ""
    wire_transfers[0].row[13] = "TBD"
    import_wire_transfer(wire_transfers[0], header_row, False)  # noqa: FBT003
    receipt.refresh_from_db()
    assert receipt.data["SAP doc # - Cash Application"] == "TBD"


def test_import_wire_transfers_update_existing_order_amount(mocker):
    """Check for update order amount and receipt"""
    mocker.patch("ecommerce.api.tasks.send_receipt_email")
    doof_email = "hdoof@odl.mit.edu"
    user = User.objects.create(email=doof_email)
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    BootcampApplicationFactory.create(
        bootcamp_run=run, user=user, state=AppStates.AWAITING_PAYMENT.value
    )

    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)

    import_wire_transfer(wire_transfers[0], header_row, False)  # noqa: FBT003
    receipt = WireTransferReceipt.objects.get(wire_transfer_id=2)
    assert receipt.data["Amount"] == "100"
    assert receipt.order.total_price_paid == 100.00
    wire_transfers[0].row[11] = "50"
    wire_transfer = WireTransfer(
        id=wire_transfers[0].id,
        learner_email=wire_transfers[0].learner_email,
        amount=Decimal(50),
        bootcamp_start_date=wire_transfers[0].bootcamp_start_date,
        bootcamp_name=wire_transfers[0].bootcamp_name,
        bootcamp_run_id=wire_transfers[0].bootcamp_run_id,
        row=wire_transfers[0].row,
    )
    with pytest.raises(CommandError):
        import_wire_transfer(wire_transfer, header_row, False)  # noqa: FBT003
    import_wire_transfer(wire_transfer, header_row, True)  # noqa: FBT003
    receipt.refresh_from_db()
    assert receipt.data["Amount"] == "50"
    assert receipt.order.total_price_paid == 50.00


def test_import_wire_transfers_update_existing_order_user(mocker):
    """Check for update order user and receipt"""
    mocker.patch("ecommerce.api.tasks.send_receipt_email")
    doof_email = "hdoof@odl.mit.edu"
    pretty_platypus_email = "pplatypus@odl.mit.edu"
    user = User.objects.create(email=doof_email)
    pretty_platypus = User.objects.create(
        email=pretty_platypus_email, username="pplatypus"
    )
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    for _user in [user, pretty_platypus]:
        BootcampApplicationFactory.create(
            bootcamp_run=run, user=_user, state=AppStates.AWAITING_PAYMENT.value
        )

    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)

    import_wire_transfer(wire_transfers[0], header_row, False)  # noqa: FBT003
    receipt = WireTransferReceipt.objects.get(wire_transfer_id=2)
    assert receipt.data["Learner Email"] == doof_email
    assert receipt.order.user.email == doof_email
    wire_transfers[0].row[2] = wire_transfers[0].row[6] = pretty_platypus_email
    wire_transfer = WireTransfer(
        id=wire_transfers[0].id,
        learner_email=pretty_platypus_email,
        amount=wire_transfers[0].amount,
        bootcamp_start_date=wire_transfers[0].bootcamp_start_date,
        bootcamp_name=wire_transfers[0].bootcamp_name,
        bootcamp_run_id=wire_transfers[0].bootcamp_run_id,
        row=wire_transfers[0].row,
    )
    with pytest.raises(CommandError):
        import_wire_transfer(wire_transfer, header_row, False)  # noqa: FBT003
    import_wire_transfer(wire_transfer, header_row, True)  # noqa: FBT003
    receipt.refresh_from_db()
    assert receipt.data["Learner Email"] == pretty_platypus_email
    assert receipt.order.user.email == pretty_platypus_email


def test_import_wire_transfers_update_existing_order_bootcamp(mocker):
    """Check for update order bootcamp and receipt"""
    mocker.patch("ecommerce.api.tasks.send_receipt_email")
    doof_email = "hdoof@odl.mit.edu"
    user = User.objects.create(email=doof_email)
    run = BootcampRunFactory.create(
        bootcamp__title="How to be Evil",
        start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_run_id="bootcamp-v1:public+SVCR-ol+R1",
    )
    bootcamp_run = BootcampRunFactory.create(
        bootcamp__title="How to be Good",
        start_date=datetime(2019, 12, 21),  # noqa: DTZ001
        bootcamp_run_id="bootcamp-v1:public+HTBG-ol+R1",
    )
    for _run in [run, bootcamp_run]:
        BootcampApplicationFactory.create(
            bootcamp_run=_run, user=user, state=AppStates.AWAITING_PAYMENT.value
        )

    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)

    import_wire_transfer(wire_transfers[0], header_row, False)  # noqa: FBT003
    receipt = WireTransferReceipt.objects.get(wire_transfer_id=2)
    assert receipt.data["Bootcamp Name"] == "How to be Evil"
    assert receipt.order.application.bootcamp_run == run
    wire_transfers[0].row[8] = "How to be Good"
    wire_transfer = WireTransfer(
        id=wire_transfers[0].id,
        learner_email=wire_transfers[0].learner_email,
        amount=Decimal(50),
        bootcamp_start_date=wire_transfers[0].bootcamp_start_date,
        bootcamp_name="How to be Good",
        bootcamp_run_id="bootcamp-v1:public+HTBG-ol+R1",
        row=wire_transfers[0].row,
    )
    with pytest.raises(CommandError):
        import_wire_transfer(wire_transfer, header_row, False)  # noqa: FBT003
    import_wire_transfer(wire_transfer, header_row, True)  # noqa: FBT003
    receipt.refresh_from_db()
    assert receipt.data["Bootcamp Name"] == "How to be Good"
    assert receipt.order.application.bootcamp_run == bootcamp_run


def test_import_wire_transfers(mocker):
    """import_wire_transfers should iterate through the list of wire transfers, processing one at a time"""
    import_mock = mocker.patch("ecommerce.api.import_wire_transfer")
    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    import_wire_transfers(csv_path)
    wire_transfers, header_row = parse_wire_transfer_csv(csv_path)
    for wire_transfer in wire_transfers:
        import_mock.assert_any_call(wire_transfer, header_row, False)  # noqa: FBT003


def test_import_wire_transfers_error(mocker):
    """import_wire_transfers should reraise errors"""
    mocker.patch("ecommerce.api.import_wire_transfer", side_effect=ZeroDivisionError)
    csv_path = Path(__file__).parent / "testdata" / "example_wire_transfers.csv"
    with pytest.raises(WireTransferImportException):
        import_wire_transfers(csv_path)
