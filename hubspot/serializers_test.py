"""Test for hubspot serializers"""

import pytest

from applications.constants import AppStates, VALID_SUBMISSION_TYPE_CHOICES, SUBMISSION_TYPE_STATE
from applications.factories import BootcampApplicationFactory, BootcampRunApplicationStepFactory, \
    ApplicationStepSubmissionFactory, ApplicationStepFactory
from hubspot.api import format_hubspot_id
from hubspot.serializers import HubspotProductSerializer, HubspotDealSerializer, \
    HubspotLineSerializer
from klasses.factories import PersonalPriceFactory, InstallmentFactory
from klasses.models import Bootcamp

pytestmark = [pytest.mark.django_db]


def test_product_serializer():
    """Test that the HubspotProductSerializer correctly serializes a Bootcamp"""
    bootcamp = Bootcamp.objects.create(title='test bootcamp 123')
    serialized_data = {'title': bootcamp.title}
    data = HubspotProductSerializer(instance=bootcamp).data
    assert data == serialized_data


def test_deal_serializer_with_personal_price():
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/personal price"""
    application = BootcampApplicationFactory.create(state=AppStates.AWAITING_PAYMENT)
    personal_price = PersonalPriceFactory.create(bootcamp_run=application.bootcamp_run, user=application.user)

    serialized_data = {'application_stage': application.state,
                       'bootcamp_name': application.bootcamp_run.bootcamp.title,
                       'price': personal_price.price.to_eng_string(),
                       'purchaser': format_hubspot_id(application.user.profile.id),
                       'name': f'Bootcamp-application-order-{application.id}',
                       'status': 'checkout_pending'}
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_with_installment_price():
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/installment price"""
    application = BootcampApplicationFactory.create(state=AppStates.AWAITING_RESUME)
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)

    serialized_data = {'application_stage': application.state,
                       'bootcamp_name': application.bootcamp_run.bootcamp.title,
                       'price': installment.amount.to_eng_string(),
                       'purchaser': format_hubspot_id(application.user.profile.id),
                       'name': f'Bootcamp-application-order-{application.id}',
                       'status': 'checkout_pending'}
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_deal_serializer_awaiting_submissions():
    """Test that the HubspotDealSerializer correctly returns the correct application stage"""
    application = BootcampApplicationFactory.create(state=AppStates.AWAITING_USER_SUBMISSIONS)
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)
    app_steps = [
        ApplicationStepFactory.create(submission_type=VALID_SUBMISSION_TYPE_CHOICES[0][0]),
        ApplicationStepFactory.create(submission_type=VALID_SUBMISSION_TYPE_CHOICES[1][0]),
    ]
    run_steps = [
        BootcampRunApplicationStepFactory.create(bootcamp_run=application.bootcamp_run, application_step=app_steps[0]),
        BootcampRunApplicationStepFactory.create(bootcamp_run=application.bootcamp_run, application_step=app_steps[1]),
    ]
    ApplicationStepSubmissionFactory(bootcamp_application=application, run_application_step=run_steps[0])

    serialized_data = {'application_stage': SUBMISSION_TYPE_STATE.get(run_steps[1].application_step.submission_type),
                       'bootcamp_name': application.bootcamp_run.bootcamp.title,
                       'price': installment.amount.to_eng_string(),
                       'purchaser': format_hubspot_id(application.user.profile.id),
                       'name': f'Bootcamp-application-order-{application.id}',
                       'status': 'checkout_pending'}
    data = HubspotDealSerializer(instance=application).data
    assert data == serialized_data


def test_line_serializer():
    """Test that the HubspotLineSerializer correctly serializes a PersonalPrice"""
    application = BootcampApplicationFactory.create()
    serialized_data = {'order': format_hubspot_id(application.integration_id),
                       'product': format_hubspot_id(application.bootcamp_run.bootcamp_id)}
    data = HubspotLineSerializer(instance=application).data
    assert data == serialized_data
