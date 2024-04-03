"""
Management command to configure custom Hubspot properties for Contacts, Deals, Products, and Line Items
"""

import sys

from django.core.management import BaseCommand
from mitol.hubspot_api.api import (
    delete_object_property,
    delete_property_group,
    object_property_exists,
    property_group_exists,
    sync_object_property,
    sync_property_group,
)

# Hubspot ecommerce settings define which hubspot_sync properties are mapped with which
# local properties when objects are synced.
# See https://developers.hubspot.com/docs/methods/ecomm-bridge/ecomm-bridge-overview for more details

CUSTOM_ECOMMERCE_PROPERTIES = {
    "deals": {
        "groups": [],
        "properties": [
            {
                "description": "Total price paid for the order.",
                "fieldType": "text",
                "groupName": "dealinformation",
                "label": "Total price paid",
                "name": "total_price_paid",
                "type": "number",
            },
            {
                "description": "The current stage of the application",
                "fieldType": "text",
                "groupName": "dealinformation",
                "label": "Application Stage",
                "name": "application_stage",
                "type": "string",
            },
            {
                "description": "The associated bootcamp name",
                "fieldType": "text",
                "groupName": "dealinformation",
                "label": "Bootcamp Name",
                "name": "bootcamp_name",
                "type": "string",
            },
            {
                "name": "unique_app_id",
                "label": "Unique App ID",
                "description": "The unique app ID for the deal",
                "groupName": "dealinformation",
                "type": "string",
                "fieldType": "text",
                "hasUniqueValue": True,
                "hidden": True,
            },
        ],
    },
    "line_items": {
        "groups": [],
        "properties": [
            {
                "name": "unique_app_id",
                "label": "Unique App ID",
                "description": "The unique app ID for the lineitem",
                "groupName": "lineiteminformation",
                "type": "string",
                "fieldType": "text",
                "hasUniqueValue": True,
                "hidden": True,
            },
        ],
    },
    "contacts": {
        "groups": [],
        "properties": [
            {
                "name": "full_name",
                "label": "Full Name",
                "description": "Full name",
                "groupName": "contactinformation",
                "type": "string",
                "fieldType": "text",
            },
            {
                "name": "highest_education",
                "label": "Highest Education",
                "description": "Highest education level",
                "groupName": "contactinformation",
                "type": "string",
                "fieldType": "text",
            },
            {
                "name": "birth_year",
                "label": "Year of Birth",
                "description": "Year of birth",
                "groupName": "contactinformation",
                "type": "string",
                "fieldType": "text",
            },
            {
                "description": "Once you heard about the program, what made you decide to apply?",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Why Apply To the Program",
                "name": "why_apply",
                "type": "string",
            },
            {
                "description": "Are you an MIT Bootcamp alumni?",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Is a Bootcamp Alumni",
                "name": "alumni",
                "type": "string",
            },
            {
                "description": "Nationality",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Nationality",
                "name": "nationality",
                "type": "string",
            },
            {
                "description": "If you were referred by MIT Bootcamps alumni, please list their name(s) below:",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Referred By",
                "name": "referred_by",
                "type": "string",
            },
            {
                "description": "Work Experience",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Work Experience",
                "name": "work_experience",
                "type": "string",
            },
            {
                "description": "What other programs have you applied to?",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Other Programs Applied To",
                "name": "other_programs",
                "type": "string",
            },
            {
                "description": "Once your admission and participation is confirmed, "
                "your fellow Bootcampers will see the links you provided above.",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Agree to Make Links Public",
                "name": "agree_see_links",
                "type": "string",
            },
            {
                "description": "Media, Participant Release & License Release",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Release Approved",
                "name": "participant_license_release",
                "type": "string",
            },
            {
                "description": 'MIT Bootcamps Honor Code (Select "I agree" to continue)',
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Agreed To Honor Code",
                "name": "mit_honor_code",
                "type": "string",
            },
            {
                "description": "Occupation",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Occupation",
                "name": "occupation",
                "type": "string",
            },
            {
                "description": "Confidentiality and IP Rights",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Confidentiality and IP Rights",
                "name": "confidentiality",
                "type": "string",
            },
            {
                "description": "Referral Information",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Referral Information",
                "name": "referral_information",
                "type": "string",
            },
            {
                "description": "How did you first hear about the Bootcamp?",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "How did you first hear about the Bootcamp?",
                "name": "hear_about_bootcamp",
                "type": "string",
            },
            {
                "description": "Highest Level of Education",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Highest Level of Education",
                "name": "highest_education",
                "type": "string",
            },
            {
                "description": "Linkedin profile URL",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Linkedin profile URL",
                "name": "linkedin_profile",
                "type": "string",
            },
            {
                "description": "Liability Release & Waiver",
                "fieldType": "text",
                "groupName": "contactinformation",
                "label": "Liability Release And Waiver",
                "name": "liability_release",
                "type": "string",
            },
        ],
    },
    "products": {
        "groups": [],
        "properties": [
            {
                "description": "Bootcamp Run ID",
                "fieldType": "text",
                "groupName": "productinformation",
                "label": "Bootcamp Run ID",
                "name": "bootcamp_run_id",
                "type": "string",
            },
            {
                "name": "unique_app_id",
                "label": "Unique App ID",
                "description": "The unique app ID for the product",
                "groupName": "productinformation",
                "type": "string",
                "fieldType": "text",
                "hasUniqueValue": True,
                "hidden": True,
            },
        ],
    },
}


def upsert_custom_properties():
    """Create or update all custom properties and groups"""
    for object_type in CUSTOM_ECOMMERCE_PROPERTIES:
        for group in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["groups"]:
            sys.stdout.write(f"Adding group {group}\n")
            sync_property_group(object_type, group["name"], group["label"])
        for obj_property in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["properties"]:
            sys.stdout.write(f"Adding property {obj_property}\n")
            sync_object_property(object_type, obj_property)


def delete_custom_properties():
    """Delete all custom properties and groups"""
    for object_type in CUSTOM_ECOMMERCE_PROPERTIES:
        for obj_property in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["properties"]:
            if object_property_exists(object_type, obj_property):
                delete_object_property(object_type, obj_property)
        for group in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["groups"]:
            if property_group_exists(object_type, group):
                delete_property_group(object_type, group)


class Command(BaseCommand):
    """
    Command to create/update or delete custom hubspot object properties and property groups
    """

    help = "Upsert or delete custom properties and property groups for Hubspot objects"

    def add_arguments(self, parser):
        """
        Definition of arguments this command accepts
        """
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete custom hubspot properties/groups",
        )

    def handle(self, *args, **options):
        if options["delete"]:
            print("Uninstalling custom groups and properties...")
            delete_custom_properties()
            print("Uninstall successful")
            return
        else:
            print("Configuring custom groups and properties...")
            upsert_custom_properties()
            print("Custom properties configured")
