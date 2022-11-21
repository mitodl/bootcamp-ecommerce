"""Test for hubspot_sync serializers"""
from decimal import Decimal

import pytest
from django.contrib.contenttypes.models import ContentType
from mitol.hubspot_api.models import HubspotObject

from applications.constants import SUBMISSION_TYPE_STATE, AppStates
from applications.factories import BootcampApplicationFactory
from ecommerce.factories import LineFactory, OrderFactory
from ecommerce.models import Order
from hubspot_sync.constants import HUBSPOT_DEAL_PREFIX
from hubspot_sync.serializers import (
    HubspotDealSerializer,
    HubspotLineSerializer,
    HubspotProductSerializer,
)
from klasses.factories import (
    BootcampRunFactory,
    InstallmentFactory,
    PersonalPriceFactory,
)
from klasses.models import BootcampRun

pytestmark = [pytest.mark.django_db]


def test_product_serializer(settings):
    """Test that the HubspotProductSerializer correctly serializes a Bootcamp"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = "test-bc"
    bootcamp_run = BootcampRunFactory.create(title="test bootcamp 123")
    serialized_data = {
        "name": bootcamp_run.title,
        "bootcamp_run_id": bootcamp_run.bootcamp_run_id,
        "unique_app_id": f"test-bc-{bootcamp_run.id}",
    }
    data = HubspotProductSerializer(instance=bootcamp_run).data
    assert data == serialized_data


@pytest.mark.parametrize(
    "pay_amount,status, prefix",
    [
        ["0.00", "checkout_completed", "abc123"],
        ["50.00", "shipped", "prefix"],
        ["1.00", "processed", "zde-123"],
        [None, "checkout_pending", ""],
    ],
)
def test_deal_serializer_with_personal_price(settings, pay_amount, status, prefix):
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/personal price"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = prefix
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
        "amount": personal_price.price.to_eng_string(),
        "dealname": f"{HUBSPOT_DEAL_PREFIX}-{application.id}",
        "dealstage": status,
        "pipeline": settings.HUBSPOT_PIPELINE_ID,
        "unique_app_id": f"{prefix}-{application.id}",
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


def test_deal_serializer_with_installment_price(settings):
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/installment price"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = "bc"
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_RESUME.value
    )
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)

    serialized_data = {
        "application_stage": application.state,
        "bootcamp_name": application.bootcamp_run.title,
        "amount": installment.amount.to_eng_string(),
        "dealname": f"{HUBSPOT_DEAL_PREFIX}-{application.id}",
        "dealstage": "checkout_pending",
        "pipeline": settings.HUBSPOT_PIPELINE_ID,
        "unique_app_id": f"bc-{application.id}",
    }
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_with_no_price(settings):
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/no price"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = "bootcamp"
    application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_RESUME.value
    )

    serialized_data = {
        "application_stage": application.state,
        "bootcamp_name": application.bootcamp_run.title,
        "amount": "0.00",
        "dealname": f"{HUBSPOT_DEAL_PREFIX}-{application.id}",
        "dealstage": "checkout_pending",
        "pipeline": settings.HUBSPOT_PIPELINE_ID,
        "unique_app_id": f"bootcamp-{application.id}",
    }
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_awaiting_submissions(settings, awaiting_submission_app):
    """Test that the HubspotDealSerializer correctly returns the correct application stage"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = "bootcamps"
    serialized_data = {
        "application_stage": SUBMISSION_TYPE_STATE.get(
            awaiting_submission_app.run_steps[1].application_step.submission_type
        ),
        "bootcamp_name": awaiting_submission_app.application.bootcamp_run.title,
        "amount": awaiting_submission_app.installment.amount.to_eng_string(),
        "dealname": f"{HUBSPOT_DEAL_PREFIX}-{awaiting_submission_app.application.id}",
        "dealstage": "checkout_pending",
        "pipeline": settings.HUBSPOT_PIPELINE_ID,
        "unique_app_id": f"bootcamps-{awaiting_submission_app.application.id}",
    }
    data = HubspotDealSerializer(instance=awaiting_submission_app.application).data
    assert data == serialized_data


def test_line_serializer(settings, hubspot_application):
    """Test that the HubspotLineSerializer correctly serializes a"""
    settings.MITOL_HUBSPOT_API_ID_PREFIX = "boot"
    line = hubspot_application.line
    serialized_data = HubspotLineSerializer(instance=line).data
    assert serialized_data == {
        "hs_product_id": HubspotObject.objects.get(
            content_type=ContentType.objects.get_for_model(BootcampRun),
            object_id=line.application.bootcamp_run.id,
        ).hubspot_id,
        "quantity": "1",
        "name": line.application.bootcamp_run.title,
        "unique_app_id": f"boot-{line.id}",
    }
