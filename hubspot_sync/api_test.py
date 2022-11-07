"""
Hubspot API tests
"""
import pytest

from hubspot_sync import api
from hubspot_sync.conftest import FAKE_HUBSPOT_ID
from hubspot_sync.serializers import (
    HubspotDealSerializer,
    HubspotLineSerializer,
    HubspotProductSerializer,
)
from klasses.factories import BootcampRunFactory

from profiles.factories import UserFactory

# pylint: disable=redefined-outer-name
pytestmark = pytest.mark.django_db


def test_make_contact_sync_message(user):
    """Test make_contact_sync_message serializes a user and returns a properly formatted sync message"""
    contact_sync_message = api.make_contact_sync_message(user.id)
    assert contact_sync_message.properties == {
        "address": "\n".join(user.legal_address.street_address),
        "birth_year": int(user.profile.birth_year),
        "city": user.legal_address.city,
        "company": user.profile.company,
        "company_size": user.profile.company_size or "",
        "country": user.legal_address.country,
        "email": user.email,
        "firstname": user.legal_address.first_name,
        "gender": user.profile.gender,
        "highest_education": user.profile.highest_education,
        "industry": user.profile.industry,
        "job_function": user.profile.job_function,
        "jobtitle": user.profile.job_title,
        "lastname": user.legal_address.last_name,
        "full_name": user.profile.name,
        "state": user.legal_address.state_or_territory,
        "zip": user.legal_address.postal_code,
    }


def test_make_deal_sync_message(hubspot_application):
    """Test make_deal_sync_message serializes a deal and returns a properly formatted sync message"""
    serialized_application = HubspotDealSerializer(hubspot_application).data
    deal_sync_message = api.make_deal_sync_message(hubspot_application.id)

    assert deal_sync_message.properties == {
        "dealname": serialized_application["dealname"],
        "dealstage": serialized_application["dealstage"],
        "application_stage": serialized_application["application_stage"],
        "bootcamp_name": serialized_application["bootcamp_name"],
        "amount": serialized_application["amount"],
        "pipeline": serialized_application["pipeline"] or "",
        "unique_app_id": serialized_application["unique_app_id"],
    }


@pytest.mark.django_db
def test_make_line_sync_message(hubspot_application):
    """Test make_line_sync_message serializes a line and returns a properly formatted sync message"""
    serialized_line = HubspotLineSerializer(hubspot_application.line).data
    line_sync_message = api.make_line_sync_message(hubspot_application.line.id)
    assert line_sync_message.properties == {
        "name": serialized_line["name"],
        "hs_product_id": serialized_line["hs_product_id"],
        "quantity": 1,
        "unique_app_id": serialized_line["unique_app_id"],
    }


@pytest.mark.django_db
def test_make_product_sync_message():
    """Test make_product_sync_message serializes a product and returns a properly formatted sync message"""
    product = BootcampRunFactory()
    serialized_product = HubspotProductSerializer(product).data
    product_sync_message = api.make_product_sync_message(product.id)

    assert product_sync_message.properties == {
        "name": product.title,
        "bootcamp_run_id": product.bootcamp_run_id,
        "unique_app_id": serialized_product["unique_app_id"],
    }


def test_sync_contact_with_hubspot(mock_hubspot_api):
    """Test that the hubspot CRM API is called properly for a contact sync"""
    user = UserFactory.create()
    api.sync_contact_with_hubspot(user.id)
    assert (
        api.HubspotObject.objects.get(
            object_id=user.id, content_type__model="user"
        ).hubspot_id
        == FAKE_HUBSPOT_ID
    )
    mock_hubspot_api.return_value.crm.objects.basic_api.create.assert_called_once_with(
        simple_public_object_input=api.make_contact_sync_message(user.id),
        object_type=api.HubspotObjectType.CONTACTS.value,
    )


def test_sync_product_with_hubspot(mock_hubspot_api):
    """Test that the hubspot CRM API is called properly for a product sync"""
    product = BootcampRunFactory.create()
    api.sync_product_with_hubspot(product.id)
    assert (
        api.HubspotObject.objects.get(
            object_id=product.id, content_type__model="bootcamprun"
        ).hubspot_id
        == FAKE_HUBSPOT_ID
    )
    mock_hubspot_api.return_value.crm.objects.basic_api.create.assert_called_once_with(
        simple_public_object_input=api.make_product_sync_message(product.id),
        object_type=api.HubspotObjectType.PRODUCTS.value,
    )


def test_sync_deal_with_hubspot(mocker, mock_hubspot_api, hubspot_application):
    """Test that the hubspot CRM API is called properly for a deal sync"""
    mock_sync_line = mocker.patch(
        "hubspot_sync.api.sync_line_item_with_hubspot", autospec=True
    )
    api.sync_deal_with_hubspot(hubspot_application.id)

    mock_hubspot_api.return_value.crm.objects.basic_api.create.assert_called_once_with(
        simple_public_object_input=api.make_deal_sync_message(hubspot_application.id),
        object_type=api.HubspotObjectType.DEALS.value,
    )

    mock_sync_line.assert_any_call(hubspot_application.line.id)

    assert (
        api.HubspotObject.objects.get(
            object_id=hubspot_application.id, content_type__model="bootcampapplication"
        ).hubspot_id
        == FAKE_HUBSPOT_ID
    )


def test_sync_line_item_with_hubspot(
    mock_hubspot_api, hubspot_application, hubspot_application_id
):
    """Test that the hubspot CRM API is called properly for a line_item sync"""
    line = hubspot_application.line
    api.sync_line_item_with_hubspot(line.id)
    assert (
        api.HubspotObject.objects.get(
            object_id=line.id, content_type__model="bootcampapplicationline"
        ).hubspot_id
        == FAKE_HUBSPOT_ID
    )
    mock_hubspot_api.return_value.crm.objects.associations_api.create.assert_called_once_with(
        api.HubspotObjectType.LINES.value,
        FAKE_HUBSPOT_ID,
        api.HubspotObjectType.DEALS.value,
        hubspot_application_id,
        api.HubspotAssociationType.LINE_DEAL.value,
    )
