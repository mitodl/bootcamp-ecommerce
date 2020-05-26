"""
Management command to sync all Users, Orders, Products, and Lines with Hubspot
and Line Items
"""
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from applications.models import BootcampApplication
from hubspot.api import (
    make_contact_sync_message,
    make_product_sync_message,
    make_deal_sync_message,
    make_line_sync_message)
from hubspot.tasks import sync_bulk_with_hubspot
from klasses.models import Bootcamp


class Command(BaseCommand):
    """
    Command to sync Contact, Product, and Deal information with Hubspot
    """

    help = (
        "Sync all Contacts, Deals, and Products with Hubspot. Hubspot API key must be set and Hubspot settings"
        "must be configured with configure_hubspot_settings"
    )

    @staticmethod
    def bulk_sync_model(objects, make_object_sync_message, object_type, **kwargs):
        """
        Sync all database objects of a certain type with hubspot
        Args:
            objects (iterable) objects to sync
            make_object_sync_message (function) function that takes an objectID and
                returns a sync message for that model
            object_type (str) one of "CONTACT", "DEAL", "PRODUCT", "LINE_ITEM"
        """
        sync_bulk_with_hubspot(objects, make_object_sync_message, object_type, print_to_console=True, **kwargs)

    def sync_contacts(self):
        """
        Sync all profiles with contacts in hubspot
        """
        print("  Syncing users with hubspot contacts...")
        self.bulk_sync_model(
            User.objects.filter(profile__isnull=False),
            make_contact_sync_message,
            "CONTACT",
        )
        print("  Finished")

    def sync_products(self):
        """
        Sync all Bootcamps with products in hubspot
        """
        print("  Syncing products with hubspot products...")
        self.bulk_sync_model(
            Bootcamp.objects.all(),
            make_product_sync_message,
            "PRODUCT",
        )
        print("  Finished")

    def sync_deals(self):
        """
        Sync all deals with deals in hubspot. Hubspot deal information is stored in both PersonalPrice
        and the ecommerce Order
        """
        print("  Syncing orders with hubspot deals...")
        self.bulk_sync_model(BootcampApplication.objects.all(), make_deal_sync_message, "DEAL")
        self.bulk_sync_model(BootcampApplication.objects.all(), make_line_sync_message, "LINE_ITEM")
        print("  Finished")

    def sync_all(self):
        """
        Sync all Users, Orders, Products, and Lines with Hubspot.
        """
        self.sync_contacts()
        self.sync_products()
        self.sync_deals()

    def add_arguments(self, parser):
        """
        Definition of arguments this command accepts
        """
        parser.add_argument(
            "--contacts",
            "--users",
            dest="sync_contacts",
            action="store_true",
            help="Sync all users",
        )
        parser.add_argument(
            "--products",
            dest="sync_products",
            action="store_true",
            help="Sync all products",
        )
        parser.add_argument(
            "--deals",
            "--orders",
            dest="sync_deals",
            action="store_true",
            help="Sync all orders",
        )

    def handle(self, *args, **options):
        print("Syncing with hubspot...")
        if not (
            options["sync_contacts"] or
            options["sync_products"] or
            options["sync_deals"]
        ):
            # If no flags are set, sync everything
            self.sync_all()
        else:
            # If some flags are set, sync the specified models
            if options["sync_contacts"]:
                self.sync_contacts()
            if options["sync_products"]:
                self.sync_products()
            if options["sync_deals"]:
                self.sync_deals()

        print("Hubspot sync complete")
