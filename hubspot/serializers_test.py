"""Test for hubspot serializers"""

import pytest

from applications.factories import BootcampApplicationFactory
from hubspot.api import format_hubspot_id
from hubspot.serializers import HubspotProductSerializer, HubspotDealSerializer, \
    HubspotLineSerializer
from klasses.factories import PersonalPriceFactory, InstallmentFactory
from klasses.models import Bootcamp
from profiles.factories import ProfileFactory

pytestmark = [pytest.mark.django_db]


def test_product_serializer():
    """Test that the HubspotProductSerializer correctly serializes a Bootcamp"""
    bootcamp = Bootcamp.objects.create(title='test bootcamp 123')
    serialized_data = {'title': bootcamp.title}
    data = HubspotProductSerializer(instance=bootcamp).data
    assert data == serialized_data


def test_deal_serializer_with_personal_price():
    """Test that the HubspotDealSerializer correctly serializes a BootcampApplication w/personal price"""
    application = BootcampApplicationFactory.create()
    personal_price = PersonalPriceFactory.create(bootcamp_run=application.bootcamp_run, user=application.user)
    profile = ProfileFactory.create()
    application.user.profile = profile

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
    application = BootcampApplicationFactory.create()
    installment = InstallmentFactory.create(bootcamp_run=application.bootcamp_run)
    profile = ProfileFactory.create()
    application.user.profile = profile

    serialized_data = {'application_stage': application.state,
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
