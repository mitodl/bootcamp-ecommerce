"""Test for hubspot serializers"""
from decimal import Decimal

import pytest

from applications.constants import AppStates, SUBMISSION_TYPE_STATE
from applications.factories import BootcampApplicationFactory
from ecommerce.factories import OrderFactory, LineFactory
from ecommerce.models import Order
from hubspot.api import format_hubspot_id
from hubspot.serializers import (
    HubspotProductSerializer,
    HubspotDealSerializer,
    HubspotLineSerializer,
)
from klasses.factories import (
    PersonalPriceFactory,
    InstallmentFactory,
    BootcampRunFactory,
)

pytestmark = [pytest.mark.django_db]


def test_product_serializer():
    """Test that the HubspotProductSerializer correctly serializes a Bootcamp"""
    bootcamp_run = BootcampRunFactory.create(title="test bootcamp 123")
    serialized_data = {
        "title": bootcamp_run.title,
        "bootcamp_run_id": bootcamp_run.bootcamp_run_id,
    }
    data = HubspotProductSerializer(instance=bootcamp_run).data
    assert data == serialized_data


@pytest.mark.parametrize(
    "pay_amount,status",
    [
        ["0.00", "checkout_completed"],
        ["50.00", "shipped"],
        ["1.00", "processed"],
        [None, "checkout_pending"],
    ],
)
def test_deal_serializer_with_personal_price(pay_amount, status):
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/personal price"""
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_PAYMENT.value
    )
    personal_price = PersonalPriceFactory.create(
        bootcamp_run=application.bootcamp_run,
        user=application.user,
        price=Decimal("50.00"),
    )
    serialized_data = {
        "application_stage": application.state,
        "bootcamp_name": application.bootcamp_run.title,
        "price": personal_price.price.to_eng_string(),
        "purchaser": format_hubspot_id(application.user.profile.id),
        "name": f"Bootcamp-application-order-{application.id}",
        "status": status,
    }
    if pay_amount is not None:
        order = OrderFactory.create(
            application=application,
            total_price_paid=pay_amount,
            user=application.user,
            status=Order.FULFILLED,
        )
        LineFactory.create(order=order, bootcamp_run=application.bootcamp_run)
        serialized_data["total_price_paid"] = pay_amount

    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_with_installment_price():
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/installment price"""
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_RESUME.value
    )
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)

    serialized_data = {
        "application_stage": application.state,
        "bootcamp_name": application.bootcamp_run.title,
        "price": installment.amount.to_eng_string(),
        "purchaser": format_hubspot_id(application.user.profile.id),
        "name": f"Bootcamp-application-order-{application.id}",
        "status": "checkout_pending",
    }
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_with_no_price():
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/no price"""
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_RESUME.value
    )

    serialized_data = {
        "application_stage": application.state,
        "bootcamp_name": application.bootcamp_run.title,
        "price": "0.00",
        "purchaser": format_hubspot_id(application.user.profile.id),
        "name": f"Bootcamp-application-order-{application.id}",
        "status": "checkout_pending",
    }
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_awaiting_submissions(awaiting_submission_app):
    """Test that the HubspotDealSerializer correctly returns the correct application stage"""
    serialized_data = {
        "application_stage": SUBMISSION_TYPE_STATE.get(
            awaiting_submission_app.run_steps[1].application_step.submission_type
        ),
        "bootcamp_name": awaiting_submission_app.application.bootcamp_run.title,
        "price": awaiting_submission_app.installment.amount.to_eng_string(),
        "purchaser": format_hubspot_id(
            awaiting_submission_app.application.user.profile.id
        ),
        "name": f"Bootcamp-application-order-{awaiting_submission_app.application.id}",
        "status": "checkout_pending",
    }
    data = HubspotDealSerializer(instance=awaiting_submission_app.application).data
    assert data == serialized_data


def test_line_serializer():
    """Test that the HubspotLineSerializer correctly serializes a PersonalPrice"""
    application = BootcampApplicationFactory.create()
    serialized_data = {
        "order": format_hubspot_id(application.integration_id),
        "product": format_hubspot_id(application.bootcamp_run.integration_id),
    }
    data = HubspotLineSerializer(instance=application).data
    assert data == serialized_data
