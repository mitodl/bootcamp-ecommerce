"""
Management command to sync all Users, BootcampRuns (deals) and Orders (BootcampApplications) with Hubspot
"""
import sys

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from mitol.common.utils import now_in_utc
from mitol.hubspot_api.api import HubspotObjectType

from hubspot_sync.tasks import batch_upsert_hubspot_deals, batch_upsert_hubspot_objects
from klasses.models import BootcampRun


class Command(BaseCommand):
    """
    Sync all Users, BootcampRuns (deals) and Orders (BootcampApplications) with Hubspot
    """

    create = None
    help = (
        "Sync all Users, Deals, Products, and Lines with Hubspot. Hubspot API key must be set and Hubspot settings"
        "must be configured with configure_hubspot_settings"
    )

    def sync_contacts(self):
        """
        Sync all users with contacts in hubspot
        """
        sys.stdout.write("Syncing users with hubspot contacts...\n")
        task = batch_upsert_hubspot_objects.delay(
            HubspotObjectType.CONTACTS.value,
            ContentType.objects.get_for_model(User).model,
            self.create,
        )
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of users to hubspot contacts finished, took {} seconds\n".format(
                total_seconds
            )
        )

    def sync_products(self):
        """
        Sync all products with products in hubspot
        """
        sys.stdout.write("  Syncing products with hubspot products...\n")
        task = batch_upsert_hubspot_objects.delay(
            HubspotObjectType.PRODUCTS.value,
            ContentType.objects.get_for_model(BootcampRun).model,
            self.create,
        )
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of products to hubspot finished, took {} seconds\n".format(
                total_seconds
            )
        )

    def sync_deals(self):
        """
        Sync all applications with deals in hubspot
        """
        sys.stdout.write("  Syncing orders with hubspot deals...\n")
        task = batch_upsert_hubspot_deals.delay(self.create)
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of orders/lines to hubspot finished, took {} seconds\n".format(
                total_seconds
            )
        )

    def sync_all(self):
        """
        Sync all Users, BootcampRuns, BootcampApplications with Hubspot.
        All products and contacts should be synced before syncing deals/line items.
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
        parser.add_argument(
            "mode",
            type=str,
            nargs="?",
            choices=["create", "update"],
            help="create or update",
        )

    def handle(self, *args, **options):
        if not options["mode"]:
            sys.stderr.write("You must specify mode ('create' or 'update')\n")
            sys.exit(1)
        self.create = options["mode"].lower() == "create"
        sys.stdout.write("Syncing with hubspot...\n")
        if not (
            options["sync_contacts"]
            or options["sync_products"]
            or options["sync_deals"]
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
        sys.stdout.write("Hubspot sync complete\n")
