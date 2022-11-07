"""Hubspot CRM API sync utilities"""
from builtins import hasattr
import logging
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from hubspot.crm.objects import (
    SimplePublicObjectInput,
)
from mitol.common.utils.collections import replace_null_values
from mitol.hubspot_api.api import (
    find_contact,
    find_deal,
    find_product,
    upsert_object_request,
    HubspotObjectType,
    associate_objects_request,
    HubspotAssociationType,
    find_line_item,
)
from mitol.hubspot_api.models import HubspotObject

from applications.constants import INTEGRATION_PREFIX
from applications.models import BootcampApplication, BootcampApplicationLine
from hubspot_sync.serializers import (
    HubspotProductSerializer,
    HubspotDealSerializer,
    HubspotLineSerializer,
)
from klasses.models import BootcampRun

log = logging.getLogger()


def parse_hubspot_deal_id(hubspot_id):
    """
    Return an object ID parsed from a hubspot_sync ID
    Args:
        hubspot_id(str): The formatted hubspot_sync ID

    Returns:
        int: The object ID or None
    """
    match = re.compile(
        fr"{settings.MITOL_HUBSPOT_API_ID_PREFIX}-{INTEGRATION_PREFIX}(\d+)"
    ).match(hubspot_id)
    return int(match.group(1)) if match else None


def make_object_properties_message(properties: dict) -> SimplePublicObjectInput:
    """
    Create data for object sync message

    Args:
        properties (dict): dict of properties to be synced

    Returns:
        SimplePublicObjectInput: input object to create/update data in Hubspot
    """
    return SimplePublicObjectInput(properties=replace_null_values(properties, ""))


def transform_object_properties(object_data: dict, mapping: dict) -> dict:
    """
    Replace model attribute names with hubspot_api property names, skip any that don't match


    Args:
        object_data (dict): serialized object data
        mapping (dict): key-value pairs of serializer to hubspot_api field names

    Returns:
        dict:  object data with hubspot_api keys


    """
    hubspot_dict = {}
    for key in object_data.keys():
        value = object_data.get(key)
        hubspot_key = mapping.get(key)
        if hubspot_key:
            hubspot_dict[hubspot_key] = value
    return hubspot_dict


def make_contact_sync_message(user_id):
    """
    Create the body of a sync message for a contact.

    Args:
        user_id (int): User id

    Returns:
        list: dict containing serializable sync-message data
    """
    from profiles.serializers import UserSerializer

    contact_properties_map = {
        "email": "email",
        "name": "full_name",
        "first_name": "firstname",
        "last_name": "lastname",
        "street_address": "address",
        "city": "city",
        "country": "country",
        "state_or_territory": "state",
        "postal_code": "zip",
        "birth_year": "birth_year",
        "gender": "gender",
        "company": "company",
        "company_size": "company_size",
        "industry": "industry",
        "job_title": "jobtitle",
        "job_function": "job_function",
        "leadership_level": "leadership_level",
        "highest_education": "highest_education",
    }

    user = User.objects.get(id=user_id)
    if not hasattr(user, "profile"):
        return [{}]
    properties = UserSerializer(user).data
    properties.update(properties.pop("legal_address") or {})
    properties.update(properties.pop("profile") or {})
    properties["work_experience"] = properties.pop("years_experience", None)
    if "street_address" in properties:
        properties["street_address"] = "\n".join(properties.pop("street_address"))
    hubspot_props = transform_object_properties(properties, contact_properties_map)
    return make_object_properties_message(hubspot_props)


def make_product_sync_message(bootcamp_run_id):
    """
    Create the body of a sync message for a product.

    Args:
        bootcamp_run_id (int): Bootcamp run id

    Returns:
        list: dict containing serializable sync-message data
    """
    bootcamp_run = BootcampRun.objects.get(id=bootcamp_run_id)
    properties = HubspotProductSerializer(instance=bootcamp_run).data
    return make_object_properties_message(properties)


def make_deal_sync_message(application_id):
    """
    Create the body of a sync message for a deal.

    Args:
        application_id (int): BootcampApplication id

    Returns:
        list: dict containing serializable sync-message data
    """
    application = BootcampApplication.objects.get(id=application_id)
    properties = HubspotDealSerializer(instance=application).data
    return make_object_properties_message(properties)


def make_line_sync_message(application_line_id):
    """
    Create the body of a sync message for a Line Item.

    Args:
        application_line_id (int):BootcampApplicationLine id

    Returns:
        list: dict containing serializable sync-message data
    """
    line = BootcampApplicationLine.objects.get(id=application_line_id)
    properties = HubspotLineSerializer(instance=line).data
    properties["quantity"] = 1
    return make_object_properties_message(properties)


def get_hubspot_id_for_object(
    obj: BootcampApplication or BootcampApplicationLine or BootcampRun or User,
    raise_error: bool = False,
):
    """
    Get the hubspot id for an object, querying Hubspot if necessary

    Args:
        obj(object): The object (BootcampApplication or BootcampRun or User) to get the id for
        raise_error(bool): raise an error if not found (default False)

    Returns:
        The hubspot id for the object if it has been previously synced to Hubspot.
        Raises a ValueError if no matching Hubspot object can be found.
    """

    content_type = ContentType.objects.get_for_model(obj)
    hubspot_obj = HubspotObject.objects.filter(
        object_id=obj.id, content_type=content_type
    ).first()
    if hubspot_obj:
        return hubspot_obj.hubspot_id
    model = obj.__class__
    if model == User:
        hubspot_obj = find_contact(obj.email)
    elif model == BootcampApplication:
        serialized_deal = HubspotDealSerializer(obj).data
        hubspot_obj = find_deal(
            name=serialized_deal["dealname"],
            amount=serialized_deal["amount"],
            raise_count_error=raise_error,
        )
    elif model == BootcampApplicationLine:
        serialized_line = HubspotLineSerializer(obj).data
        application_id = get_hubspot_id_for_object(obj.application)
        hubspot_obj = find_line_item(
            application_id,
            hs_product_id=serialized_line["hs_product_id"],
            raise_count_error=raise_error,
        )
    elif model == BootcampRun:
        serialized_product = HubspotProductSerializer(obj).data
        hubspot_obj = find_product(
            serialized_product["name"],
            raise_count_error=raise_error,
        )
    if hubspot_obj and hubspot_obj.id:
        HubspotObject.objects.update_or_create(
            object_id=obj.id,
            content_type=content_type,
            defaults={"hubspot_id": hubspot_obj.id},
        )
        return hubspot_obj.id
    elif raise_error:
        raise ValueError(
            "Hubspot id could not be found for %s for id %d"
            % (content_type.name, obj.id)
        )


def sync_contact_with_hubspot(user_id: int):
    """Sync a user with a hubspot_xpro contact"""
    body = make_contact_sync_message(user_id)
    content_type = ContentType.objects.get_for_model(User)

    return upsert_object_request(
        content_type, HubspotObjectType.CONTACTS.value, object_id=user_id, body=body
    )


def sync_product_with_hubspot(product_id: int):
    """Sync a product with a hubspot_xpro product"""
    body = make_product_sync_message(product_id)
    content_type = ContentType.objects.get_for_model(BootcampRun)

    # Check if a matching hubspot object has been or can be synced
    get_hubspot_id_for_object(BootcampRun.objects.get(id=product_id))

    return upsert_object_request(
        content_type, HubspotObjectType.PRODUCTS.value, object_id=product_id, body=body
    )


def sync_line_item_with_hubspot(line_id: int):
    """Sync a Line with a hubspot line item"""
    line = BootcampApplicationLine.objects.get(id=line_id)
    body = make_line_sync_message(line_id)
    content_type = ContentType.objects.get_for_model(BootcampApplicationLine)

    # Check if a matching hubspot object has been or can be synced
    get_hubspot_id_for_object(line)

    # Create or update the line items
    result = upsert_object_request(
        content_type, HubspotObjectType.LINES.value, object_id=line_id, body=body
    )
    # Associate the parent deal with the line item
    associate_objects_request(
        HubspotObjectType.LINES.value,
        result.id,
        HubspotObjectType.DEALS.value,
        get_hubspot_id_for_object(
            BootcampApplicationLine.objects.get(id=line_id).application
        ),
        HubspotAssociationType.LINE_DEAL.value,
    )
    return result


def sync_deal_with_hubspot(application_id: int):
    """Sync an Order with a hubspot deal"""
    application = BootcampApplication.objects.get(id=application_id)
    body = make_deal_sync_message(application_id)
    content_type = ContentType.objects.get_for_model(BootcampApplication)

    # Check if a matching hubspot object has been or can be synced
    get_hubspot_id_for_object(application)

    # Create or update the order aka deal
    result = upsert_object_request(
        content_type, HubspotObjectType.DEALS.value, object_id=application_id, body=body
    )
    # Create association between deal and contact
    associate_objects_request(
        HubspotObjectType.DEALS.value,
        result.id,
        HubspotObjectType.CONTACTS.value,
        get_hubspot_id_for_object(application.user),
        HubspotAssociationType.DEAL_CONTACT.value,
    )

    sync_line_item_with_hubspot(application.line.id)
    return result
