"""Tests for ecommerce views"""
from django.urls import (
    resolve,
    reverse,
)
import faker
import pytest
from rest_framework import status as statuses

from applications.constants import AppStates
from applications.factories import BootcampApplicationFactory
from ecommerce.api import make_reference_id
from ecommerce.api_test import (
    create_purchasable_bootcamp_run,
    create_test_order,
)
from ecommerce.exceptions import EcommerceException
from ecommerce.models import (
    Order,
    OrderAudit,
    Receipt,
)
from ecommerce.serializers import PaymentSerializer
from klasses.models import BootcampRunEnrollment
from fluidreview.api import FluidReviewException
from fluidreview.constants import WebhookParseStatus
from fluidreview.factories import WebhookRequestFactory
from profiles.factories import UserFactory

CYBERSOURCE_SECURITY_KEY = '🔑'
CYBERSOURCE_SECURE_ACCEPTANCE_URL = 'http://fake'
CYBERSOURCE_REFERENCE_PREFIX = 'fake'
FAKE = faker.Factory.create()


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def ecommerce_settings(settings):
    """Settings for ecommerce tests"""
    settings.CYBERSOURCE_SECURITY_KEY = CYBERSOURCE_SECURITY_KEY
    settings.CYBERSOURCE_SECURE_ACCEPTANCE_URL = CYBERSOURCE_SECURE_ACCEPTANCE_URL
    settings.CYBERSOURCE_REFERENCE_PREFIX = CYBERSOURCE_REFERENCE_PREFIX
    settings.ECOMMERCE_EMAIL = 'ecommerce@example.com'


def test_using_serializer_validation(client):
    """
    The view should use the serializer for validation
    """
    payment_url = reverse('create-payment')
    assert resolve(payment_url).func.view_class.serializer_class is PaymentSerializer

    # Make sure we haven't overridden something which would skip validation
    user = UserFactory.create()
    client.force_login(user)
    resp = client.post(payment_url, data={
        "payment_amount": "-1",
        "run_key": 3,
    })
    assert resp.status_code == statuses.HTTP_400_BAD_REQUEST
    assert resp.json() == {
        "payment_amount": ["Ensure this value is greater than or equal to 0.01."]
    }


def test_login_required(client):
    """Anonymous users are forbidden"""
    resp = client.post(reverse('create-payment'), data={})
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN


def test_payment(mocker, client):
    """
    If a user POSTs to the payment API an unfulfilled order should be created
    """
    bootcamp_run, user = create_purchasable_bootcamp_run()
    client.force_login(user)
    fake_payload = "fake_payload"
    fake_order = 'fake_order'
    generate_cybersource_sa_payload_mock = mocker.patch(
        'ecommerce.views.generate_cybersource_sa_payload', autospec=True, return_value=fake_payload
    )
    create_unfulfilled_order_mock = mocker.patch(
        'ecommerce.views.create_unfulfilled_order', autospec=True, return_value=fake_order
    )
    resp = client.post(reverse('create-payment'), data={
        "payment_amount": bootcamp_run.price,
        "run_key": bootcamp_run.run_key,
    })
    assert resp.status_code == statuses.HTTP_200_OK
    assert resp.json() == {
        'payload': fake_payload,
        'url': CYBERSOURCE_SECURE_ACCEPTANCE_URL,
    }
    assert generate_cybersource_sa_payload_mock.call_count == 1
    generate_cybersource_sa_payload_mock.assert_any_call(fake_order, "http://testserver/pay/")
    assert create_unfulfilled_order_mock.call_count == 1
    create_unfulfilled_order_mock.assert_any_call(user, bootcamp_run.run_key, bootcamp_run.price)


@pytest.mark.parametrize("side_effect", [None, FluidReviewException])
@pytest.mark.parametrize("has_application", [True, False])
@pytest.mark.parametrize("has_paid", [True, False])
def test_order_fulfilled(client, mocker, side_effect, has_application, has_paid):
    """
    Test the happy case
    """
    bootcamp_run, user = create_purchasable_bootcamp_run()
    user.profile.fluidreview_id = 999
    user.profile.save()
    payment = 123
    order = create_test_order(user, bootcamp_run.run_key, payment)
    WebhookRequestFactory(
        user_email=user.email,
        user_id=user.profile.fluidreview_id,
        award_id=bootcamp_run.run_key,
        status=WebhookParseStatus.SUCCEEDED
    )
    data_before = order.to_dict()

    data = {}
    for _ in range(5):
        data[FAKE.text()] = FAKE.text()

    data['req_reference_number'] = make_reference_id(order)
    data['decision'] = 'ACCEPT'
    mocker.patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=True)
    send_email = mocker.patch(
        'ecommerce.views.MailgunClient.send_individual_email',
    )
    mockapi = mocker.patch('fluidreview.api.FluidReviewAPI.put', side_effect=side_effect)
    paid_in_full_mock = mocker.patch('ecommerce.views.is_paid_in_full', return_value=has_paid)

    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_PAYMENT.value,
        order=order,
    ) if has_application else None

    resp = client.post(reverse('order-fulfillment'), data=data)

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
    paid_in_full_mock.assert_called_once_with(user=user, run_key=bootcamp_run.run_key)

    if has_application:
        application.refresh_from_db()
        assert application.state == (
            AppStates.COMPLETE.value if has_paid else AppStates.AWAITING_PAYMENT.value
        )

    assert BootcampRunEnrollment.objects.filter(bootcamp_run=bootcamp_run, user=user).count() == (
        1 if has_paid else 0
    )



def test_missing_fields(client, mocker):
    """
    If CyberSource POSTs with fields missing, we should at least save it in a receipt.
    It is very unlikely for Cybersource to POST invalid data but it also provides a way to test
    that we save a Receipt in the event of an error.
    """
    data = {}
    for _ in range(5):
        data[FAKE.text()] = FAKE.text()
    mocker.patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=True)
    try:
        # Missing fields from Cybersource POST will cause the KeyError.
        # In this test we want to make sure we saved the data in Receipt for later
        # analysis even if there is an error.
        client.post(reverse('order-fulfillment'), data=data)
    except KeyError:
        pass

    assert Order.objects.count() == 0
    assert Receipt.objects.count() == 1
    assert Receipt.objects.first().data == data


@pytest.mark.parametrize("decision, should_send_email", [
    ('CANCEL', False),
    ('something else', True),
])
def test_not_accept(mocker, client, decision, should_send_email):
    """
    If the decision is not ACCEPT then the order should be marked as failed
    """
    bootcamp_run, user = create_purchasable_bootcamp_run()
    order = create_test_order(user, bootcamp_run.run_key, 123)

    data = {
        'req_reference_number': make_reference_id(order),
        'decision': decision,
    }
    mocker.patch(
        'ecommerce.views.IsSignedByCyberSource.has_permission',
        return_value=True
    )
    send_email = mocker.patch(
        'ecommerce.views.MailgunClient.send_individual_email',
    )
    resp = client.post(reverse('order-fulfillment'), data=data)
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


def test_ignore_duplicate_cancel(client, mocker):
    """
    If the decision is CANCEL and we already have a duplicate failed order, don't change anything.
    """
    bootcamp_run, user = create_purchasable_bootcamp_run()
    order = create_test_order(user, bootcamp_run.run_key, 123)
    order.status = Order.FAILED
    order.save()

    data = {
        'req_reference_number': make_reference_id(order),
        'decision': 'CANCEL',
    }
    mocker.patch(
        'ecommerce.views.IsSignedByCyberSource.has_permission',
        return_value=True
    )
    resp = client.post(reverse('order-fulfillment'), data=data)
    assert resp.status_code == statuses.HTTP_200_OK

    assert Order.objects.count() == 1
    assert Order.objects.get(id=order.id).status == Order.FAILED


@pytest.mark.parametrize("order_status, decision", [
    (Order.FAILED, 'ERROR'),
    (Order.FULFILLED, 'ERROR'),
    (Order.FULFILLED, 'SUCCESS'),
])
def test_error_on_duplicate_order(mocker, client, order_status, decision):
    """If there is a duplicate message (except for CANCEL), raise an exception"""
    bootcamp_run, user = create_purchasable_bootcamp_run()
    order = create_test_order(user, bootcamp_run.run_key, 123)
    order.status = order_status
    order.save()

    data = {
        'req_reference_number': make_reference_id(order),
        'decision': decision,
    }
    mocker.patch(
        'ecommerce.views.IsSignedByCyberSource.has_permission',
        return_value=True
    )
    with pytest.raises(EcommerceException) as ex:
        client.post(reverse('order-fulfillment'), data=data)

    assert Order.objects.count() == 1
    assert Order.objects.get(id=order.id).status == order_status

    assert ex.value.args[0] == "Order {id} is expected to have status 'created'".format(
        id=order.id,
    )


def test_no_permission(client, mocker):
    """
    If the permission class didn't give permission we shouldn't get access to the POST
    """
    mocker.patch('ecommerce.views.IsSignedByCyberSource.has_permission', return_value=False)
    resp = client.post(reverse('order-fulfillment'), data={})
    assert resp.status_code == statuses.HTTP_403_FORBIDDEN
