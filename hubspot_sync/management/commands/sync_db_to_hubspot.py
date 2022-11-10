"""
Management command to sync all Users, BootcampRuns (deals) and Orders (BootcampApplications) with Hubspot
"""
import sys

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand
from mitol.common.utils import now_in_utc
from mitol.hubspot_api.api import HubspotObjectType

from applications.models import BootcampApplication, BootcampApplicationLine
from hubspot_sync.tasks import (
    batch_upsert_hubspot_objects,
    batch_upsert_associations,
)
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
            User._meta.app_label,
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
            BootcampRun._meta.app_label,
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
        sys.stdout.write("  Syncing applications with hubspot deals...\n")
        task = batch_upsert_hubspot_objects.delay(
            HubspotObjectType.DEALS.value,
            ContentType.objects.get_for_model(BootcampApplication).model,
            BootcampApplication._meta.app_label,
            self.create,
        )
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of orders/lines to hubspot finished, took {} seconds\n".format(
                total_seconds
            )
        )

    def sync_lines(self):
        """
        Sync all applications with line_items in hubspot
        """
        sys.stdout.write("  Syncing application lines with hubspot line_items...\n")
        task = batch_upsert_hubspot_objects.delay(
            HubspotObjectType.LINES.value,
            ContentType.objects.get_for_model(BootcampApplicationLine).model,
            BootcampApplicationLine._meta.app_label,
            self.create,
        )
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of application lines to hubspot finished, took {} seconds\n".format(
                total_seconds
            )
        )

    def sync_associations(self):
        """
        Sync all deal associations in hubspot
        """
        sys.stdout.write("  Syncing deal associations with hubspot...\n")
        task = batch_upsert_associations.delay()
        start = now_in_utc()
        task.get()
        total_seconds = (now_in_utc() - start).total_seconds()
        self.stdout.write(
            "Syncing of deal associations to hubspot finished, took {} seconds\n".format(
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
        self.sync_lines()
        self.sync_associations()

    def add_arguments(self, parser):
        """
        Definition of arguments this command accepts
        """
        parser.add_argument(
            "--users",
            "--contacts",
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
            "--applications",
            "--deals",
            dest="sync_deals",
            action="store_true",
            help="Sync all bootcamp applications (deals)",
        )
        parser.add_argument(
            "--lines",
            "--line_items",
            dest="sync_lines",
            action="store_true",
            help="Sync all application line items",
        )
        parser.add_argument(
            "--associations",
            dest="sync_associations",
            action="store_true",
            help="Sync all application associations",
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
            or options["sync_lines"]
            or options["sync_associations"]
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
            if options["sync_lines"]:
                self.sync_lines()
            if options["sync_associations"]:
                self.sync_associations()
        sys.stdout.write("Hubspot sync complete\n")
