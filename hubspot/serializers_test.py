"""Test for hubspot serializers"""

import pytest

from hubspot.api import format_hubspot_id
from hubspot.serializers import HubspotContactSerializer, HubspotProductSerializer, HubspotDealSerializer, \
    HubspotLineSerializer
from klasses.factories import PersonalPriceFactory
from klasses.models import Bootcamp
from profiles.factories import ProfileFactory

pytestmark = [pytest.mark.django_db]


def test_profile_serializer(mocker, demographics_data, task_data, serialized_data):
    """Test the HubspotProfileSerializer"""
    profile = ProfileFactory.create(smapply_id=123456)
    profile.smapply_demographic_data = demographics_data
    profile.save()

    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotContactSerializer(instance=profile).data
    assert data == serialized_data


def test_profile_serializer_no_task(mocker, user_data):
    """Test the HubspotProfileSerializer with no task data in the Profile"""
    profile = ProfileFactory.create(smapply_id=123456)
    profile.smapply_user_data = user_data
    profile.save()

    mocker.patch('smapply.api.SMApplyAPI')

    data = HubspotContactSerializer(instance=profile).data
    assert data == {'smapply_id': 123456, 'email': 'test_user@test.co',
                    'first_name': 'FirstName', 'last_name': 'LastName'}


def test_profile_serializer_missing_task_responses(mocker, demographics_data, task_data, serialized_data):
    """Test that HubspotProfileSerializer does not log error when demographics data is missing"""
    logger = mocker.patch('logging.Logger.error')
    profile = ProfileFactory.create(smapply_id=123456)
    demographics_data['data'].pop('8JgmHI7gTA')
    profile.smapply_demographic_data = demographics_data
    profile.save()
    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotContactSerializer(instance=profile).data
    logger.assert_not_called()
    serialized_data.pop('industry')
    assert data == serialized_data


def test_profile_serializer_missing_task_fields(mocker, demographics_data, task_data, serialized_data):
    """Test that HubspotProfileSerializer does not log error when demographics data is missing"""
    logger = mocker.patch('logging.Logger.error')
    profile = ProfileFactory.create(smapply_id=123456)
    demographics_data['data'].pop('8JgmHI7gTA')
    profile.smapply_demographic_data = demographics_data
    profile.save()
    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    task_data['fields'].pop('8JgmHI7gTA')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotContactSerializer(instance=profile).data
    logger.assert_not_called()
    serialized_data.pop('industry')
    assert data == serialized_data


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
                       'bootcamp_name': personal_price.klass.bootcamp.title,
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
                       'product': format_hubspot_id(personal_price.klass.bootcamp_id)}
    data = HubspotLineSerializer(instance=personal_price).data
    assert data == serialized_data
