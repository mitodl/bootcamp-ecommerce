"""Test for hubspot serializers"""

import pytest

from hubspot.api import format_hubspot_id
from hubspot.serializers import HubspotProductSerializer, HubspotDealSerializer, \
    HubspotLineSerializer
from klasses.factories import PersonalPriceFactory
from klasses.models import Bootcamp
from profiles.factories import ProfileFactory

pytestmark = [pytest.mark.django_db]


def test_product_serializer():
    """Test that the HubspotProductSerializer correctly serializes a Bootcamp"""
    bootcamp = Bootcamp.objects.create(title='test bootcamp 123')
    serialized_data = {'title': bootcamp.title}
    data = HubspotProductSerializer(instance=bootcamp).data
    assert data == serialized_data


def test_deal_serializer():
    """Test that the HubspotDealSerializer correctly serializes a PersonalPrice"""
    personal_price = PersonalPriceFactory.create()
    profile = ProfileFactory.create()
    personal_price.user.profile = profile

    serialized_data = {'application_stage': '',
                       'bootcamp_name': personal_price.bootcamp_run.bootcamp.title,
                       'price': personal_price.price.to_eng_string(),
                       'purchaser': format_hubspot_id(personal_price.user.profile.id),
                       'name': f'Bootcamp-application-{personal_price.id}',
                       'status': 'checkout_pending'}
    data = HubspotDealSerializer(instance=personal_price).data
    assert data == serialized_data


def test_line_serializer():
    """Test that the HubspotLineSerializer correctly serializes a PersonalPrice"""
    personal_price = PersonalPriceFactory.create()
    profile = ProfileFactory.create()
    personal_price.user.profile = profile

    serialized_data = {'order': format_hubspot_id(personal_price.id),
                       'product': format_hubspot_id(personal_price.bootcamp_run.bootcamp_id)}
    data = HubspotLineSerializer(instance=personal_price).data
    assert data == serialized_data
