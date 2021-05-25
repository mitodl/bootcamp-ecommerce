"""Tests for ecommerce views"""
from unittest.mock import PropertyMock

from django.urls import resolve, reverse
import faker
import pytest
from rest_framework import status as statuses

from applications.constants import AppStates, VALID_APP_STATE_CHOICES
from applications.factories import BootcampApplicationFactory
from backends.edxorg import EdxOrgOAuth2
from ecommerce.api import make_reference_id
from ecommerce.exceptions import EcommerceException
from ecommerce.factories import LineFactory, OrderFactory
from ecommerce.models import Order, OrderAudit, Receipt
from ecommerce.serializers import (
    CheckoutDataSerializer,
    PaymentSerializer,
    OrderSerializer,
)
from ecommerce.test_utils import create_test_application, create_test_order
from ecommerce.views import OrderView
from klasses.factories import BootcampRunFactory
from klasses.models import BootcampRunEnrollment
from profiles.factories import ProfileFactory, UserFactory


CYBERSOURCE_SECURITY_KEY = "🔑"
CYBERSOURCE_SECURE_ACCEPTANCE_URL = "http://fake"
CYBERSOURCE_REFERENCE_PREFIX = "fake"
FAKE = faker.Factory.create()


pytestmark = pytest.mark.django_db


# pylint: disable=unused-argument,too-many-locals,redefined-outer-name
@pytest.fixture(autouse=True)
def ecommerce_settings(settings):
    """Settings for ecommerce tests"""
    settings.CYBERSOURCE_SECURITY_KEY = CYBERSOURCE_SECURITY_KEY
    settings.CYBERSOURCE_SECURE_ACCEPTANCE_URL = CYBERSOURCE_SECURE_ACCEPTANCE_URL
    settings.CYBERSOURCE_REFERENCE_PREFIX = CYBERSOURCE_REFERENCE_PREFIX
    settings.ECOMMERCE_EMAIL = "ecommerce@example.com"


@pytest.fixture(autouse=True)
def patched_novoed_tasks(mocker):
    """Fixture to patch novoed tasks"""
    mocker.patch("klasses.api.novoed_tasks")


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


def test_using_serializer_validation(client):
    """
    The view should use the serializer for validation
    """
    payment_url = reverse("create-payment")
    assert resolve(payment_url).func.view_class.serializer_class is PaymentSerializer

    # Make sure we haven't overridden something which would skip validation
    user = UserFactory.create()
    client.force_login(user)
    resp = client.post(payment_url, data={"payment_amount": "-1", "application_id": 3})
    assert resp.status_code == statuses.HTTP_400_BAD_REQUEST
    assert resp.json() == {
        "payment_amount": ["Ensure this value is greater than or equal to 0.01."]
    }


def test_login_required(client):
    """Anonymous users are forbidden"""
    resp = client.post(reverse("create-payment"), data={})
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN


def test_payment(mocker, client, user, bootcamp_run, application):
    """
    If a user POSTs to the payment API an unfulfilled order should be created
    """
    client.force_login(user)
    fake_payload = "fake_payload"
    fake_order = OrderFactory.create(
        application=BootcampApplicationFactory.create(
            bootcamp_run=bootcamp_run, user=user
        )
    )
    fake_ip = "195.0.0.1"

    mock_ip_call = mocker.patch(
        "ecommerce.views.get_client_ip", return_value=(fake_ip, True)
    )

    generate_cybersource_sa_payload_mock = mocker.patch(
        "ecommerce.views.generate_cybersource_sa_payload",
        autospec=True,
        return_value=fake_payload,
    )
    create_unfulfilled_order_mock = mocker.patch(
        "ecommerce.views.create_unfulfilled_order",
        autospec=True,
        return_value=fake_order,
    )
    resp = client.post(
        reverse("create-payment"),
        data={"payment_amount": bootcamp_run.price, "application_id": application.id},
    )
    assert resp.status_code == statuses.HTTP_200_OK
    assert resp.json() == {
        "payload": fake_payload,
        "url": CYBERSOURCE_SECURE_ACCEPTANCE_URL,
    }
    assert mock_ip_call.call_count == 1
    assert generate_cybersource_sa_payload_mock.call_count == 1
    generate_cybersource_sa_payload_mock.assert_any_call(
        fake_order, "http://testserver/applications/", fake_ip
    )
    assert create_unfulfilled_order_mock.call_count == 1
    create_unfulfilled_order_mock.assert_any_call(
        application=application, payment_amount=bootcamp_run.price
    )


@pytest.mark.parametrize(
    "state",
    [
        state
        for state, _ in VALID_APP_STATE_CHOICES
        if state != AppStates.AWAITING_PAYMENT.value
    ],
)
def test_payment_invalid_state(client, state, application, user, bootcamp_run):
    """
    A user should only be able to pay if the application state is AWAITING_PAYMENT
    """
    application.state = state
    application.save()

    client.force_login(user)
    resp = client.post(
        reverse("create-payment"),
        data={"payment_amount": bootcamp_run.price, "application_id": application.id},
    )
    assert resp.status_code == statuses.HTTP_400_BAD_REQUEST
    assert resp.json() == ["Invalid application state"]


# pylint: disable=too-many-arguments
@pytest.mark.parametrize("has_paid", [True, False])
def test_order_fulfilled(client, mocker, application, bootcamp_run, user, has_paid):
    """
    Test the happy case
    """
    payment = 123
    order = create_test_order(application, payment, fulfilled=False)
    order.application = BootcampApplicationFactory.create(
        bootcamp_run=bootcamp_run, user=user, state=AppStates.AWAITING_PAYMENT.value
    )
    order.save()
    data_before = order.to_dict()

    data = {}
    for _ in range(5):
        data[FAKE.text()] = FAKE.text()

    data["req_reference_number"] = make_reference_id(order)
    data["decision"] = "ACCEPT"
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=True
    )
    send_email = mocker.patch("ecommerce.api.MailgunClient.send_individual_email")
    mock_tasks = mocker.patch("ecommerce.api.tasks")
    paid_in_full_mock = mocker.patch(
        "applications.models.BootcampApplication.is_paid_in_full",
        new_callable=PropertyMock,
    )
    paid_in_full_mock.return_value = has_paid

    resp = client.post(reverse("order-fulfillment"), data=data)

    assert len(resp.content) == 0
    assert resp.status_code == statuses.HTTP_200_OK
    order.refresh_from_db()
    assert order.status == Order.FULFILLED
    assert order.receipt_set.count() == 1
    assert order.receipt_set.first().data == data

    assert send_email.call_count == 0
    assert OrderAudit.objects.count() == 2
    order_audit = OrderAudit.objects.last()
    assert order_audit.order == order
    assert order_audit.data_before == data_before
    assert order_audit.data_after == order.to_dict()

    order.application.refresh_from_db()
    assert order.application.state == (
        AppStates.COMPLETE.value if has_paid else AppStates.AWAITING_PAYMENT.value
    )
    assert (
        BootcampRunEnrollment.objects.filter(
            bootcamp_run=order.application.bootcamp_run, user=order.application.user
        ).exists()
        is has_paid
    )

    mock_tasks.send_receipt_email.delay.assert_called_once_with(order.application.id)


def test_missing_fields(client, mocker):
    """
    If CyberSource POSTs with fields missing, we should at least save it in a receipt.
    It is very unlikely for Cybersource to POST invalid data but it also provides a way to test
    that we save a Receipt in the event of an error.
    """
    data = {}
    for _ in range(5):
        data[FAKE.text()] = FAKE.text()
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=True
    )
    try:
        # Missing fields from Cybersource POST will cause the KeyError.
        # In this test we want to make sure we saved the data in Receipt for later
        # analysis even if there is an error.
        client.post(reverse("order-fulfillment"), data=data)
    except KeyError:
        pass

    assert Order.objects.count() == 0
    assert Receipt.objects.count() == 1
    assert Receipt.objects.first().data == data


@pytest.mark.parametrize(
    "decision, should_send_email", [("CANCEL", False), ("something else", True)]
)
def test_not_accept(mocker, client, application, decision, should_send_email):
    """
    If the decision is not ACCEPT then the order should be marked as failed
    """
    order = create_test_order(application, 123, fulfilled=False)

    data = {"req_reference_number": make_reference_id(order), "decision": decision}
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=True
    )
    send_email = mocker.patch("ecommerce.api.MailgunClient.send_individual_email")
    resp = client.post(reverse("order-fulfillment"), data=data)
    assert resp.status_code == statuses.HTTP_200_OK
    assert len(resp.content) == 0
    order.refresh_from_db()
    assert Order.objects.count() == 1
    assert order.status == Order.FAILED

    if should_send_email:
        assert send_email.call_count == 1
        assert send_email.call_args[0] == (
            "Order fulfillment failed, decision={decision}".format(
                decision="something else"
            ),
            "Order fulfillment failed for order {order}".format(order=order),
            "ecommerce@example.com",
        )
    else:
        assert send_email.call_count == 0


def test_ignore_duplicate_cancel(client, mocker, application):
    """
    If the decision is CANCEL and we already have a duplicate failed order, don't change anything.
    """
    order = create_test_order(application, 123, fulfilled=False)
    order.status = Order.FAILED
    order.save()

    data = {"req_reference_number": make_reference_id(order), "decision": "CANCEL"}
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=True
    )
    resp = client.post(reverse("order-fulfillment"), data=data)
    assert resp.status_code == statuses.HTTP_200_OK

    assert Order.objects.count() == 1
    assert Order.objects.get(id=order.id).status == Order.FAILED


@pytest.mark.parametrize(
    "order_status, decision",
    [(Order.FAILED, "ERROR"), (Order.FULFILLED, "ERROR"), (Order.FULFILLED, "SUCCESS")],
)
def test_error_on_duplicate_order(mocker, client, application, order_status, decision):
    """If there is a duplicate message (except for CANCEL), raise an exception"""
    order = create_test_order(application, 123, fulfilled=False)
    order.status = order_status
    order.save()

    data = {"req_reference_number": make_reference_id(order), "decision": decision}
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=True
    )
    with pytest.raises(EcommerceException) as ex:
        client.post(reverse("order-fulfillment"), data=data)

    assert Order.objects.count() == 1
    assert Order.objects.get(id=order.id).status == order_status

    assert ex.value.args[0] == "Order {id} is expected to have status 'created'".format(
        id=order.id
    )


def test_no_permission(client, mocker):
    """
    If the permission class didn't give permission we shouldn't get access to the POST
    """
    mocker.patch(
        "ecommerce.views.IsSignedByCyberSource.has_permission", return_value=False
    )
    resp = client.post(reverse("order-fulfillment"), data={})
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN


BOOTCAMP_RUN_FIELDS = [
    "run_key",
    "start_date",
    "end_date",
    "total_paid",
    "installments",
    "payments",
    "bootcamp_run_name",
    "display_title",
    "price",
]


@pytest.fixture()
def test_data():
    """
    Sets up the data for all the tests in this module
    """
    profile = ProfileFactory.create()
    user = profile.user
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid=user.username,
        extra_data={"access_token": "fooooootoken"},
    )
    other_user = ProfileFactory.create().user

    for _ in range(3):
        bootcamp_run = BootcampRunFactory.create()
    BootcampApplicationFactory.create(
        bootcamp_run=bootcamp_run, user=user, state=AppStates.AWAITING_PAYMENT.value
    )

    # just need one bootcamp run, so returning the last created
    return user, other_user, bootcamp_run


@pytest.fixture()
def fulfilled_order(test_data):
    """Create a fulfilled order for testing"""
    user, _, bootcamp_run = test_data
    order = OrderFactory.create(user=user, status=Order.FULFILLED)
    LineFactory.create(order=order, bootcamp_run=bootcamp_run, price=123.45)
    return order


def test_only_self_can_access_apis(test_data, client):
    """
    Only the the requester user can access her own info
    """
    user, other_user, bootcamp_run = test_data
    detail_url_user = reverse(
        "bootcamp-run-detail",
        kwargs={"username": user.username, "run_key": bootcamp_run.run_key},
    )
    detail_url_other_user = reverse(
        "bootcamp-run-detail",
        kwargs={"username": other_user.username, "run_key": bootcamp_run.run_key},
    )
    list_url_user = reverse("bootcamp-run-list", kwargs={"username": user.username})
    list_url_other_user = reverse(
        "bootcamp-run-list", kwargs={"username": other_user.username}
    )

    # anonymous
    for url in (
        detail_url_user,
        detail_url_other_user,
        list_url_user,
        list_url_other_user,
    ):
        assert client.get(url).status_code == statuses.HTTP_403_FORBIDDEN

    client.force_login(other_user)
    assert client.get(detail_url_user).status_code == statuses.HTTP_403_FORBIDDEN
    assert client.get(detail_url_other_user).status_code == statuses.HTTP_404_NOT_FOUND
    assert client.get(list_url_user).status_code == statuses.HTTP_403_FORBIDDEN
    assert client.get(list_url_other_user).status_code == statuses.HTTP_404_NOT_FOUND

    client.force_login(user)
    assert client.get(detail_url_user).status_code == statuses.HTTP_200_OK
    assert client.get(detail_url_other_user).status_code == statuses.HTTP_404_NOT_FOUND
    assert client.get(list_url_user).status_code == statuses.HTTP_200_OK
    assert client.get(list_url_other_user).status_code == statuses.HTTP_404_NOT_FOUND


def test_bootcamp_run_detail(test_data, client):
    """
    Test for bootcamp run detail view in happy path
    """
    user, _, bootcamp_run = test_data
    bootcamp_run_detail_url = reverse(
        "bootcamp-run-detail",
        kwargs={"username": user.username, "run_key": bootcamp_run.run_key},
    )
    client.force_login(user)

    response = client.get(bootcamp_run_detail_url)
    assert response.status_code == statuses.HTTP_200_OK
    response_json = response.json()
    assert sorted(list(response_json.keys())) == sorted(BOOTCAMP_RUN_FIELDS)
    assert response_json["run_key"] == bootcamp_run.run_key


def test_bootcamp_run_detail_fake_run(test_data, client):
    """
    Test if a request is made for a not existing bootcamp run
    """
    user, _, _ = test_data
    bootcamp_run_detail_url = reverse(
        "bootcamp-run-detail",
        kwargs={"username": user.username, "run_key": 123_456_789},
    )
    client.force_login(user)
    assert (
        client.get(bootcamp_run_detail_url).status_code == statuses.HTTP_404_NOT_FOUND
    )


def test_bootcamp_run_list(test_data, client):
    """
    Test for bootcamp run list view in happy path
    """
    user, _, _ = test_data
    bootcamp_run_list_url = reverse(
        "bootcamp-run-list", kwargs={"username": user.username}
    )
    client.force_login(user)

    response = client.get(bootcamp_run_list_url)
    assert response.status_code == statuses.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    for resp in response_json:
        assert sorted(list(resp.keys())) == sorted(BOOTCAMP_RUN_FIELDS)


def test_user_bootcamp_run_statement(test_data, fulfilled_order, client):
    """
    Test that the user bootcamp run statement view returns the expected filled-in template
    """
    user, _, bootcamp_run = test_data
    bootcamp_run_statement_url = reverse(
        "bootcamp-run-statement", kwargs={"run_key": bootcamp_run.run_key}
    )
    client.force_login(user)

    response = client.get(bootcamp_run_statement_url)
    assert response.status_code == statuses.HTTP_200_OK
    assert response.template_name == "bootcamp/statement.html"
    rendered_template_content = response.content.decode("utf-8")
    # User's full name should be in the statement
    assert response.data["user"]["full_name"] in rendered_template_content
    # Bootcamp run title should be in the statement
    assert response.data["bootcamp_run"]["display_title"] in rendered_template_content
    # Total payment amount should be in the statement
    assert (
        "${}".format(response.data["bootcamp_run"]["total_paid"])
        in rendered_template_content
    )
    # Each individual payment should be in the statement
    line_payments = fulfilled_order.line_set.values_list("price", flat=True)
    for line_payment in line_payments:
        assert "${}".format(line_payment) in rendered_template_content


def test_user_bootcamp_run_statement_without_order(test_data, client):
    """If there is no order, the bootcamp run statement view should return a 404"""
    user, _, bootcamp_run = test_data
    bootcamp_run_statement_url = reverse(
        "bootcamp-run-statement", kwargs={"run_key": bootcamp_run.run_key}
    )
    client.force_login(user)

    response = client.get(bootcamp_run_statement_url)
    assert response.status_code == statuses.HTTP_404_NOT_FOUND


def test_checkout_data(mocker, client):
    """The checkout data API should return serialized application data"""
    app_awaiting_payment = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_PAYMENT.value
    )
    user = app_awaiting_payment.user
    # An application a different state should be filtered out
    BootcampApplicationFactory.create(state=AppStates.AWAITING_RESUME.value, user=user)
    mock_request = mocker.Mock(user=user)

    client.force_login(user)
    url = f'{reverse("checkout-data-detail")}?application={app_awaiting_payment.id}'
    resp = client.get(url)

    assert (
        resp.json()
        == CheckoutDataSerializer(
            instance=app_awaiting_payment, context={"request": mock_request}
        ).data
    )


def test_checkout_data_no_application_id(client, user):
    """check that the application query parameter is required"""
    client.force_login(user)
    resp = client.get(reverse("checkout-data-detail"))
    assert resp.status_code == statuses.HTTP_404_NOT_FOUND


def test_checkout_data_anonymous(client):
    """anonymous users cannot query the checkout data API"""
    resp = client.get(reverse("checkout-data-detail"))
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN


def test_order_view_permissions(client, user):
    """A user should not be able to access order data if it does not belong to them"""
    random_user = UserFactory.create(is_staff=False, is_superuser=False)
    order = OrderFactory.create(user=user)
    client.force_login(random_user)
    resp = client.get(reverse("order-api", kwargs={"pk": order.id}))
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN
    order.user = random_user
    order.save()
    resp = client.get(reverse("order-api", kwargs={"pk": order.id}))
    assert resp.status_code == statuses.HTTP_200_OK


def test_order_view_serializer():
    """The OrderView should use the expected serializer"""
    assert OrderView.serializer_class == OrderSerializer
