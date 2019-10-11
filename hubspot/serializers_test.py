"""Test for hubspot serializers"""

import pytest

from hubspot.serializers import HubspotProfileSerializer
from profiles.factories import ProfileFactory

pytestmark = [pytest.mark.django_db]


def test_profile_serializer(mocker, demographics_data, task_data, serialized_data):
    """Test the HubspotProfileSerializer"""
    profile = ProfileFactory.create(smapply_id=123456)
    profile.smapply_demographic_data = demographics_data
    profile.save()

    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotProfileSerializer(instance=profile).data
    assert data == serialized_data


def test_profile_serializer_no_task(mocker, user_data):
    """Test the HubspotProfileSerializer with no task data in the Profile"""
    profile = ProfileFactory.create(smapply_id=123456)
    profile.smapply_user_data = user_data
    profile.save()

    mocker.patch('smapply.api.SMApplyAPI')

    data = HubspotProfileSerializer(instance=profile).data
    assert data == {'smapply_id': 123456, 'email': 'test_user@test.co',
                    'first_name': 'FirstName', 'last_name': 'LastName'}


def test_profile_serializer_missing_task_responses(mocker, demographics_data, task_data, serialized_data):
    """Test that HubspotProfileSerializer properly logs an error when demographics data is missing"""
    logger = mocker.patch('logging.Logger.error')
    profile = ProfileFactory.create(smapply_id=123456)
    demographics_data['data'].pop('8JgmHI7gTA')
    profile.smapply_demographic_data = demographics_data
    profile.save()
    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotProfileSerializer(instance=profile).data
    logger.assert_called_once()
    serialized_data.pop('industry')
    assert data == serialized_data


def test_profile_serializer_missing_task_fields(mocker, demographics_data, task_data, serialized_data):
    """Test that HubspotProfileSerializer properly logs an error when demographics data is missing"""
    logger = mocker.patch('logging.Logger.error')
    profile = ProfileFactory.create(smapply_id=123456)
    demographics_data['data'].pop('8JgmHI7gTA')
    profile.smapply_demographic_data = demographics_data
    profile.save()
    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    task_data['fields'].pop('8JgmHI7gTA')
    mock_api().get.return_value.json.return_value = task_data

    data = HubspotProfileSerializer(instance=profile).data
    logger.assert_called_once()
    serialized_data.pop('industry')
    assert data == serialized_data
