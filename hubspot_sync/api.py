"""Hubspot CRM API sync utilities"""
import logging
import re
from builtins import hasattr
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.validators import validate_email
from hubspot.crm.objects import SimplePublicObject, SimplePublicObjectInput
from mitol.common.utils.collections import replace_null_values
from mitol.hubspot_api.api import (
    HubspotApi,
    HubspotAssociationType,
    HubspotObjectType,
    associate_objects_request,
    find_contact,
    find_deal,
    find_line_item,
    find_product,
    get_all_objects,
    get_line_items_for_deal,
    upsert_object_request,
)
from mitol.hubspot_api.models import HubspotObject

from applications.constants import INTEGRATION_PREFIX
from applications.models import BootcampApplication, BootcampApplicationLine
from hubspot_sync.serializers import (
    HubspotDealSerializer,
    HubspotLineSerializer,
    HubspotProductSerializer,
)
from klasses.models import BootcampRun

log = logging.getLogger()


def parse_hubspot_deal_id(hubspot_id) -> int:
    """
    Return an object ID parsed from a hubspot ID
    Args:
        hubspot_id(str): The formatted hubspot ID

    Returns:
        int: The object ID or None
    """
    match = re.compile(
        rf"{settings.MITOL_HUBSPOT_API_ID_PREFIX}-{INTEGRATION_PREFIX}(\d+)"
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
    if isinstance(obj, User) and validate_email(obj.email):
        hubspot_obj = find_contact(obj.email)
    elif isinstance(obj, BootcampApplication):
        serialized_deal = HubspotDealSerializer(obj).data
        hubspot_obj = find_deal(
            name=serialized_deal["dealname"],
            amount=serialized_deal["amount"],
            raise_count_error=raise_error,
        )
    elif isinstance(obj, BootcampApplicationLine):
        serialized_line = HubspotLineSerializer(obj).data
        application_id = get_hubspot_id_for_object(obj.application)
        hubspot_obj = find_line_item(
            application_id,
            hs_product_id=serialized_line["hs_product_id"],
            raise_count_error=raise_error,
        )
    elif isinstance(obj, BootcampRun):
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


def sync_contact_with_hubspot(user_id: int) -> SimplePublicObject:
    """
    Sync a user with a hubspot contact

    Args:
        user_id(int): The User id

    Returns:
        SimplePublicObject: The hubspot contact object
    """
    body = make_contact_sync_message(user_id)
    content_type = ContentType.objects.get_for_model(User)

    return upsert_object_request(
        content_type, HubspotObjectType.CONTACTS.value, object_id=user_id, body=body
    )


def sync_product_with_hubspot(product_id: int) -> SimplePublicObject:
    """
    Sync a Product with a hubspot product

    Args:
        product_id(int): The Product id

    Returns:
        SimplePublicObject: The hubspot product object
    """
    body = make_product_sync_message(product_id)
    content_type = ContentType.objects.get_for_model(BootcampRun)

    # Check if a matching hubspot object has been or can be synced
    get_hubspot_id_for_object(BootcampRun.objects.get(id=product_id))

    return upsert_object_request(
        content_type, HubspotObjectType.PRODUCTS.value, object_id=product_id, body=body
    )


def sync_line_item_with_hubspot(line_id: int) -> SimplePublicObject:
    """
    Sync a Line with a hubspot line item

    Args:
        line_id(int): The Line id

    Returns:
        SimplePublicObject: The hubspot line_item object
    """
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


def sync_deal_with_hubspot(application_id: int) -> SimplePublicObject:
    """
    Sync an Order with a hubspot deal

    Args:
        order_id(int): The Order id

    Returns:
        SimplePublicObject: The hubspot deal object
    """
    application = BootcampApplication.objects.get(id=application_id)
    body = make_deal_sync_message(application_id)
    content_type = ContentType.objects.get_for_model(BootcampApplication)

    # Check if a matching hubspot object has been or can be synced
    get_hubspot_id_for_object(application)

    # Create or update the order aka deal
    result = upsert_object_request(
        content_type, HubspotObjectType.DEALS.value, object_id=application_id, body=body
    )
    # Create association between deal and contact if any
    contact = get_hubspot_id_for_object(application.user)
    if contact:
        associate_objects_request(
            HubspotObjectType.DEALS.value,
            result.id,
            HubspotObjectType.CONTACTS.value,
            contact,
            HubspotAssociationType.DEAL_CONTACT.value,
        )

    sync_line_item_with_hubspot(application.line.id)
    return result


def sync_contact_hubspot_ids_to_db():
    """
    Create HubspotObjects for all contacts in Hubspot

    Returns:
        bool: True if hubspot id matches found for all Users
    """
    contacts = get_all_objects(
        HubspotObjectType.CONTACTS.value, properties=["email", "hs_additional_emails"]
    )
    content_type = ContentType.objects.get_for_model(User)
    active_users = User.objects.filter(is_active=True)
    for contact in contacts:
        user = active_users.filter(email=contact.properties["email"]).first()
        if not user and contact.properties["hs_additional_emails"]:
            user = active_users.filter(
                email__in=contact.properties["hs_additional_emails"].split(";")
            ).first()
        if user:
            HubspotObject.objects.update_or_create(
                content_type=content_type,
                object_id=user.id,
                defaults={"hubspot_id": contact.id},
            )
    return (
        active_users.count()
        == HubspotObject.objects.filter(content_type=content_type).count()
    )


def sync_product_hubspot_ids_to_db() -> bool:
    """
    Create HubspotObjects for BootcampRuns, return True if all BootcampRuns have hubspot ids

    Returns:
        bool: True if hubspot id matches found for all BootcampRuns
    """
    content_type = ContentType.objects.get_for_model(BootcampRun)
    product_mapping = {}
    for bootcamp_run in BootcampRun.objects.all():
        product_mapping.setdefault(bootcamp_run.title, []).append(bootcamp_run.id)
    products = get_all_objects(
        HubspotObjectType.PRODUCTS.value, properties=["name", "bootcamp_run_id"]
    )
    for product in products:
        matching_runs = product_mapping.get(product.properties["name"])
        if not matching_runs:
            continue
        if len(matching_runs) > 1:
            # Narrow down by price
            for obj_id in matching_runs:
                if (
                    BootcampRun.objects.get(id=obj_id).bootcamp_run_id
                    == product.properties["bootcamp_run_id"]
                ):
                    matching_run = obj_id
        else:
            matching_run = matching_runs[0]
        HubspotObject.objects.update_or_create(
            content_type=content_type,
            object_id=matching_run,
            defaults={"hubspot_id": product.id},
        )
    return (
        BootcampRun.objects.count()
        == HubspotObject.objects.filter(content_type=content_type).count()
    )


def sync_deal_line_hubspot_ids_to_db(application, hubspot_application_id) -> bool:
    """
    Create HubspotObjects for all of a deal's line items, return True if matches found for all lines

    Args:
        application(Order or B2BOrder): The order to sync Hubspot line items for
        hubspot_application_id(str): The Hubspot deal id

    Returns:
        bool: True if matches found for all the order lines

    """
    client = HubspotApi()
    line_items = get_line_items_for_deal(hubspot_application_id)
    application_line = application.line

    matches = 0
    if len(line_items) == 1:
        HubspotObject.objects.update_or_create(
            content_type=ContentType.objects.get_for_model(application_line),
            object_id=application_line.id,
            defaults={"hubspot_id": line_items[0].id},
        )
        matches += 1
    else:  # Multiple lines, need to match by product (BootcampRun)
        for line in line_items:
            details = client.crm.line_items.basic_api.get_by_id(line.id)
            hs_product = HubspotObject.objects.filter(
                hubspot_id=details.properties["hs_product_id"],
                content_type=ContentType.objects.get_for_model(BootcampRun),
            ).first()
            if hs_product:
                product_id = hs_product.object_id
                matching_line = BootcampApplicationLine.objects.filter(
                    application=application,
                    application__bootcamp_run__id=product_id,
                ).first()
                if matching_line:
                    HubspotObject.objects.update_or_create(
                        content_type=ContentType.objects.get_for_model(
                            BootcampApplicationLine
                        ),
                        object_id=matching_line.id,
                        defaults={"hubspot_id": line.id},
                    )
                    matches += 1
    return matches == 1


def sync_deal_hubspot_ids_to_db() -> bool:
    """
    Create Hubspot objects for bootcamp applications, return True if all applications
    (and optionally lines) have hubspot ids

    Returns:
        bool: True if matches found for all Orders and B2BOrders (and optionally their lines)
    """
    content_type = ContentType.objects.get_for_model(BootcampApplication)
    deals = get_all_objects(
        HubspotObjectType.DEALS.value, properties=["dealname", "amount"]
    )
    lines_synced = True
    for deal in deals:
        deal_name = deal.properties["dealname"]
        deal_price = Decimal(deal.properties["amount"] or "0.00")
        try:
            object_id = int(deal_name.split("-")[-1])
        except ValueError:
            # this isn't a deal that can be synced, ie "AMx Run 3 - SPIN MASTER"
            continue
        applications = list(BootcampApplication.objects.filter(id=object_id))
        if len(applications) > 1:
            applications = [
                application
                for application in applications
                if application.price == deal_price
            ]
        if applications:
            application = applications[0]
            HubspotObject.objects.update_or_create(
                content_type=content_type,
                object_id=application.id,
                defaults={"hubspot_id": deal.id},
            )
            if not sync_deal_line_hubspot_ids_to_db(application, deal.id):
                lines_synced = False
    return (
        BootcampApplication.objects.count()
        == HubspotObject.objects.filter(content_type=content_type).count()
        and lines_synced
    )


MODEL_FUNCTION_MAPPING = {
    "user": make_contact_sync_message,
    "bootcampapplication": make_deal_sync_message,
    "bootcampapplicationline": make_line_sync_message,
    "bootcamprun": make_product_sync_message,
}
