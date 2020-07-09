"""Import a wire transfer spreadsheet"""
import csv

from django.core.management import BaseCommand
from django.db import transaction

from ecommerce.api import import_wire_transfers


class Command(BaseCommand):
    """Import a CSV of wire transfer transactions"""

    help = "Import a CSV of wire transfer transactions"

    def add_arguments(self, parser):
        """Handle arguments"""
        parser.add_argument("csv_path", type=str, help="Path to the CSV")

    def handle(self, *args, **options):
        """Import CSV of wire transfers"""
        import_wire_transfers(options["csv_path"])
