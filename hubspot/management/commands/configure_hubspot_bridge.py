"""
Management command to configure the Hubspot ecommerce bridge which handles syncing Contacts, Deals, Products,
and Line Items
"""
import json
from django.core.management import BaseCommand

from hubspot.api import (
    send_hubspot_request,
    property_group_exists,
    sync_property_group,
    sync_object_property,
    delete_object_property,
    delete_property_group,
    object_property_exists,
)

# Hubspot ecommerce settings define which hubspot properties are mapped with which
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
            }
        ],
    },
}

HUBSPOT_ECOMMERCE_SETTINGS = {
    "enabled": True,
    "productSyncSettings": {
        "properties": [
            {
                "propertyName": "title",
                "targetHubspotProperty": "name",
                "dataType": "STRING",
            },
            {
                "propertyName": "bootcamp_run_id",
                "targetHubspotProperty": "bootcamp_run_id",
                "dataType": "STRING",
            },
        ]
    },
    "dealSyncSettings": {
        "properties": [
            {
                "propertyName": "name",
                "targetHubspotProperty": "dealname",
                "dataType": "STRING",
            },
            {
                "propertyName": "price",
                "targetHubspotProperty": "amount",
                "dataType": "NUMBER",
            },
            {
                "propertyName": "total_price_paid",
                "targetHubspotProperty": "total_price_paid",
                "dataType": "NUMBER",
            },
            {
                "propertyName": "close_date",
                "targetHubspotProperty": "closedate",
                "dataType": "STRING",
            },
            {
                "propertyName": "purchaser",
                "targetHubspotProperty": "hs_assoc__contact_ids",
                "dataType": "STRING",
            },
            {
                "propertyName": "status",
                "targetHubspotProperty": "dealstage",
                "dataType": "STRING",
            },
            {
                "propertyName": "application_stage",
                "targetHubspotProperty": "application_stage",
                "dataType": "STRING",
            },
            {
                "propertyName": "bootcamp_name",
                "targetHubspotProperty": "bootcamp_name",
                "dataType": "STRING",
            },
        ]
    },
    "lineItemSyncSettings": {
        "properties": [
            {
                "propertyName": "order",
                "targetHubspotProperty": "hs_assoc__deal_id",
                "dataType": "STRING",
            },
            {
                "propertyName": "product",
                "targetHubspotProperty": "hs_assoc__product_id",
                "dataType": "STRING",
            },
            {
                "propertyName": "quantity",
                "targetHubspotProperty": "quantity",
                "dataType": "NUMBER",
            },
        ]
    },
    "contactSyncSettings": {
        "properties": [
            {
                "propertyName": "email",
                "targetHubspotProperty": "email",
                "dataType": "STRING",
            },
            {
                "propertyName": "name",
                "targetHubspotProperty": "full_name",
                "dataType": "STRING",
            },
            {
                "propertyName": "first_name",
                "targetHubspotProperty": "firstname",
                "dataType": "STRING",
            },
            {
                "propertyName": "last_name",
                "targetHubspotProperty": "lastname",
                "dataType": "STRING",
            },
            {
                "propertyName": "phone",
                "targetHubspotProperty": "phone",
                "dataType": "STRING",
            },
            {
                "propertyName": "company",
                "targetHubspotProperty": "company",
                "dataType": "STRING",
            },
            {
                "propertyName": "jobtitle",
                "targetHubspotProperty": "jobtitle",
                "dataType": "STRING",
            },
            {
                "propertyName": "street_address",
                "targetHubspotProperty": "address",
                "dataType": "STRING",
            },
            {
                "propertyName": "city",
                "targetHubspotProperty": "city",
                "dataType": "STRING",
            },
            {
                "propertyName": "country",
                "targetHubspotProperty": "country",
                "dataType": "STRING",
            },
            {
                "propertyName": "state_or_territory",
                "targetHubspotProperty": "state",
                "dataType": "STRING",
            },
            {
                "propertyName": "postal_code",
                "targetHubspotProperty": "zip",
                "dataType": "STRING",
            },
            {
                "propertyName": "birth_year",
                "targetHubspotProperty": "birth_year",
                "dataType": "STRING",
            },
            {
                "propertyName": "gender",
                "targetHubspotProperty": "gender",
                "dataType": "STRING",
            },
            {
                "propertyName": "company",
                "targetHubspotProperty": "company",
                "dataType": "STRING",
            },
            {
                "propertyName": "company_size",
                "targetHubspotProperty": "company_size",
                "dataType": "STRING",
            },
            {
                "propertyName": "industry",
                "targetHubspotProperty": "industry",
                "dataType": "STRING",
            },
            {
                "propertyName": "date_of_birth",
                "targetHubspotProperty": "date_of_birth",
                "dataType": "STRING",
            },
            {
                "propertyName": "job_title",
                "targetHubspotProperty": "jobtitle",
                "dataType": "STRING",
            },
            {
                "propertyName": "job_function",
                "targetHubspotProperty": "job_function",
                "dataType": "STRING",
            },
            {
                "propertyName": "years_experience",
                "targetHubspotProperty": "years_experience",
                "dataType": "STRING",
            },
            {
                "propertyName": "highest_education",
                "targetHubspotProperty": "highest_education",
                "dataType": "STRING",
            },
            {
                "propertyName": "why_apply",
                "targetHubspotProperty": "why_apply",
                "dataType": "STRING",
            },
            {
                "propertyName": "alumni",
                "targetHubspotProperty": "alumni",
                "dataType": "STRING",
            },
            {
                "propertyName": "nationality",
                "targetHubspotProperty": "nationality",
                "dataType": "STRING",
            },
            {
                "propertyName": "referred_by",
                "targetHubspotProperty": "referred_by",
                "dataType": "STRING",
            },
            {
                "propertyName": "work_experience",
                "targetHubspotProperty": "work_experience",
                "dataType": "STRING",
            },
            {
                "propertyName": "other_programs",
                "targetHubspotProperty": "other_programs",
                "dataType": "STRING",
            },
            {
                "propertyName": "agree_see_links",
                "targetHubspotProperty": "agree_see_links",
                "dataType": "STRING",
            },
            {
                "propertyName": "participant_license_release",
                "targetHubspotProperty": "participant_license_release",
                "dataType": "STRING",
            },
            {
                "propertyName": "mit_honor_code",
                "targetHubspotProperty": "mit_honor_code",
                "dataType": "STRING",
            },
            {
                "propertyName": "occupation",
                "targetHubspotProperty": "occupation",
                "dataType": "STRING",
            },
            {
                "propertyName": "confidentiality",
                "targetHubspotProperty": "confidentiality",
                "dataType": "STRING",
            },
            {
                "propertyName": "referral_information",
                "targetHubspotProperty": "referral_information",
                "dataType": "STRING",
            },
            {
                "propertyName": "hear_about_bootcamp",
                "targetHubspotProperty": "hear_about_bootcamp",
                "dataType": "STRING",
            },
            {
                "propertyName": "highest_education",
                "targetHubspotProperty": "highest_education",
                "dataType": "STRING",
            },
            {
                "propertyName": "linkedin_profile",
                "targetHubspotProperty": "linkedin_profile",
                "dataType": "STRING",
            },
            {
                "propertyName": "liability_release",
                "targetHubspotProperty": "liability_release",
                "dataType": "STRING",
            },
        ]
    },
}

HUBSPOT_INSTALL_PATH = "/extensions/ecomm/v1/installs"
HUBSPOT_SETTINGS_PATH = "/extensions/ecomm/v1/settings"


def install_hubspot_ecommerce_bridge():
    """Install the Hubspot ecommerce bridge for the api key specified in settings"""
    response = send_hubspot_request("", HUBSPOT_INSTALL_PATH, "POST")
    response.raise_for_status()
    return response


def uninstall_hubspot_ecommerce_bridge():
    """Install the Hubspot ecommerce bridge for the api key specified in settings"""
    response = send_hubspot_request("uninstall", HUBSPOT_INSTALL_PATH, "POST")
    response.raise_for_status()
    return response


def get_hubspot_installation_status():
    """Get the Hubspot ecommerce bridge installation status for the api key specified in settings"""
    response = send_hubspot_request("status", HUBSPOT_INSTALL_PATH, "GET")
    response.raise_for_status()
    return response


def configure_hubspot_settings():
    """Configure the current Hubspot ecommerce bridge settings for the api key specified in settings"""
    response = send_hubspot_request(
        "", HUBSPOT_SETTINGS_PATH, "PUT", body=HUBSPOT_ECOMMERCE_SETTINGS
    )
    response.raise_for_status()
    return response


def install_custom_properties():
    """Create or update all custom properties and groups"""
    for object_type in CUSTOM_ECOMMERCE_PROPERTIES:
        for group in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["groups"]:
            sync_property_group(object_type, group["name"], group["label"])
        for obj_property in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["properties"]:
            sync_object_property(object_type, obj_property)


def uninstall_custom_properties():
    """Delete all custom properties and groups"""
    for object_type in CUSTOM_ECOMMERCE_PROPERTIES:
        for obj_property in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["properties"]:
            if object_property_exists(object_type, obj_property):
                delete_object_property(object_type, obj_property)
        for group in CUSTOM_ECOMMERCE_PROPERTIES[object_type]["groups"]:
            if property_group_exists(object_type, group):
                delete_property_group(object_type, group)


def get_hubspot_settings():
    """Get the current Hubspot ecommerce bridge settings for the api key specified in settings"""
    response = send_hubspot_request("", HUBSPOT_SETTINGS_PATH, "GET")
    response.raise_for_status()
    return response


class Command(BaseCommand):
    """
    Command to configure the Hubspot ecommerce bridge which will handle syncing Hubspot Products, Deals, Line Items,
    and Contacts with the MITxPro Products, Orders, and Users
    """

    help = (
        "Install the Hubspot Ecommerce Bridge if it is not already installed and configure the settings based on "
        "the given file. Make sure a HUBSPOT_API_KEY is set in settings and HUBSPOT_ECOMMERCE_SETTINGS are "
        "configured in ecommerce/management/commands/configure_hubspot_bridge.py"
    )

    def add_arguments(self, parser):
        """
        Definition of arguments this command accepts
        """
        parser.add_argument(
            "--uninstall", action="store_true", help="Uninstall the Ecommerce Bridge"
        )

        parser.add_argument(
            "--status",
            action="store_true",
            help="Get the current status of the Ecommerce Bridge installation",
        )

    def handle(self, *args, **options):
        print(
            "Checking Hubspot Ecommerce Bridge installation for given Hubspot API Key..."
        )
        installation_status = json.loads(get_hubspot_installation_status().text)
        print(installation_status)
        if options["status"]:
            print(f"Install completed: {installation_status['installCompleted']}")
            print(
                f"Ecommerce Settings enabled: {installation_status['ecommSettingsEnabled']}"
            )
        elif options["uninstall"]:
            if installation_status["installCompleted"]:
                print("Uninstalling Ecommerce Bridge...")
                uninstall_hubspot_ecommerce_bridge()
                print("Uninstalling cutsom groups and properties...")
                uninstall_custom_properties()
                print("Uninstall successful")
                return
            else:
                print("Ecommerce Bridge is not installed")
                return
        else:
            print("Configuring settings...")
            configure_hubspot_settings()
            print("Configuring custom groups and properties...")
            install_custom_properties()
            print("Settings and custom properties configured")
