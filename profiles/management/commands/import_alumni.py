"""Import a alumni spreadsheet"""

from django.core.management.base import BaseCommand

from profiles.api import import_alumni


class Command(BaseCommand):
    """Import a csv of bootcamp alumni"""

    help = "Import a csv of bootcamp alumni"

    def add_arguments(self, parser):
        """Handle arguments"""
        parser.add_argument("csv_path", type=str, help="path to the csv")

    def handle(self, *args, **options):  # noqa: ARG002
        """Import a csv of bootcamp alumni"""
        import_alumni(options["csv_path"])
