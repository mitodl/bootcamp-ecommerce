"""
Hubspot API tests
"""
import pytest
from django.contrib.contenttypes.models import ContentType
from mitol.hubspot_api.factories import HubspotObjectFactory, SimplePublicObjectFactory
from mitol.hubspot_api.models import HubspotObject

from applications.factories import BootcampApplicationFactory
from applications.models import BootcampApplication, BootcampApplicationLine
from hubspot_sync import api
from hubspot_sync.conftest import FAKE_HUBSPOT_ID
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


@pytest.mark.parametrize("match_all", [True, False])
def test_sync_contact_hubspot_ids_to_hubspot(mocker, mock_hubspot_api, match_all):
    """sync_contact_hubspot_ids_to_hubspot should create HubspotObjects and return True if all users matched"""
    matches = 3 if match_all else 2
    users = UserFactory.create_batch(3)
    contacts = [
        SimplePublicObjectFactory(properties={"email": user.email})
        for user in users[0:matches]
    ]
    mock_hubspot_api.return_value.crm.objects.basic_api.get_page.side_effect = [
        mocker.Mock(results=contacts, paging=None)
    ]
    assert api.sync_contact_hubspot_ids_to_db() is match_all
    assert HubspotObject.objects.filter(content_type__model="user").count() == matches


@pytest.mark.parametrize("multiple_emails", [True, False])
def test_sync_contact_hubspot_ids_alternate(mocker, mock_hubspot_api, multiple_emails):
    """sync_contact_hubspot_ids_to_hubspot should be able to match by alternate emails"""
    user = UserFactory.create()
    additional_emails = (
        f"{user.email};other_email@fake.edu" if multiple_emails else user.email
    )
    contacts = [
        SimplePublicObjectFactory(
            properties={
                "hs_additional_emails": additional_emails,
                "email": "fake@fake.edu",
            }
        )
    ]
    mock_hubspot_api.return_value.crm.objects.basic_api.get_page.side_effect = [
        mocker.Mock(results=contacts, paging=None)
    ]
    assert api.sync_contact_hubspot_ids_to_db() is True
    assert HubspotObject.objects.filter(content_type__model="user").count() == 1


@pytest.mark.parametrize("match_all", [True, False])
def test_sync_product_hubspot_ids_to_hubspot(mocker, mock_hubspot_api, match_all):
    """sync_product_hubspot_ids_to_db should create HubspotObjects and return True if all products matched"""
    matches = 3 if match_all else 2
    db_runs = BootcampRunFactory.create_batch(3)
    hs_products = [
        SimplePublicObjectFactory(properties={"name": bootcamp_run.title})
        for bootcamp_run in db_runs[0:matches]
    ]
    mock_hubspot_api.return_value.crm.objects.basic_api.get_page.side_effect = [
        mocker.Mock(results=hs_products, paging=None)
    ]
    assert api.sync_product_hubspot_ids_to_db() is match_all
    assert (
        HubspotObject.objects.filter(
            content_type=ContentType.objects.get_for_model(BootcampRun)
        ).count()
        == matches
    )


def test_sync_product_hubspot_ids_dupe_names(mocker, mock_hubspot_api):
    """sync_product_hubspot_ids_to_db should handle dupe product names"""
    bootcamp_runs = BootcampRunFactory.create_batch(2, title="Same Name Product")
    db_run_installments = [
        InstallmentFactory.create(bootcamp_run=bootcamp_run)
        for bootcamp_run in bootcamp_runs
    ]
    assert BootcampRun.objects.count() == 2
    assert db_run_installments[0].amount != db_run_installments[1].amount
    assert db_run_installments[0].bootcamp_run != db_run_installments[1].bootcamp_run
    hs_products = [
        SimplePublicObjectFactory(
            properties={
                "name": installment.bootcamp_run.title,
                "bootcamp_run_id": installment.bootcamp_run.bootcamp_run_id,
            }
        )
        for installment in db_run_installments
    ]
    mock_hubspot_api.return_value.crm.objects.basic_api.get_page.side_effect = [
        mocker.Mock(results=hs_products, paging=None)
    ]
    assert api.sync_product_hubspot_ids_to_db() is True
    assert (
        HubspotObject.objects.filter(
            content_type=ContentType.objects.get_for_model(BootcampRun)
        ).count()
        == 2
    )


@pytest.mark.parametrize("match_all_lines", [True, False])
@pytest.mark.parametrize("match_all_deals", [True, False])
def test_sync_deal_hubspot_ids_to_hubspot(
    mocker, mock_hubspot_api, match_all_deals, match_all_lines
):
    """sync_deal_hubspot_ids_to_hubspot should create HubspotObjects and return True if all deals & lines matched"""
    deal_matches = 3 if match_all_deals else 2
    line_matches = 3 if match_all_lines else 2
    applications = BootcampApplicationFactory.create_batch(3)
    for application in applications:
        PersonalPriceFactory.create(
            bootcamp_run=application.bootcamp_run, user=application.user
        )
    deals = [
        SimplePublicObjectFactory(
            properties={
                "dealname": f"{HUBSPOT_DEAL_PREFIX}-{application.id}",
                "amount": str(application.price),
            }
        )
        for application in applications[0:deal_matches]
    ]
    # This deal should be ignored
    SimplePublicObjectFactory(
        properties={
            "dealname": f"{HUBSPOT_DEAL_PREFIX}-MANUAL",
            "amount": "400.00",
        }
    )
    hs_products = [
        HubspotObjectFactory.create(
            content_object=application.bootcamp_run,
            content_type=ContentType.objects.get_for_model(BootcampRun),
            object_id=application.bootcamp_run.id,
        )
        for application in applications
    ]
    line_items = [
        SimplePublicObjectFactory(
            properties={"hs_product_id": hsp.hubspot_id, "quantity": 1}
        )
        for hsp in hs_products[0:line_matches]
    ]
    mock_hubspot_api.return_value.crm.objects.basic_api.get_page.side_effect = [
        mocker.Mock(results=deals, paging=None),  # deals
    ]
    mock_hubspot_api.return_value.crm.deals.associations_api.get_all.side_effect = [
        *[mocker.Mock(results=[SimplePublicObjectFactory()]) for _ in line_items],
        mocker.Mock(results=[]),
    ]  # associations
    mock_hubspot_api.return_value.crm.line_items.basic_api.get_by_id.side_effect = [
        SimplePublicObjectFactory(properties={"hs_product_id": hsp.hubspot_id})
        for hsp in hs_products[0:line_matches]
    ]  # line_item details
    assert api.sync_deal_hubspot_ids_to_db() is (match_all_lines and match_all_deals)
    assert (
        HubspotObject.objects.filter(
            content_type=ContentType.objects.get_for_model(BootcampApplication)
        ).count()
        == deal_matches
    )
    assert HubspotObject.objects.filter(
        content_type=ContentType.objects.get_for_model(BootcampApplicationLine)
    ).count() == min(deal_matches, line_matches)
