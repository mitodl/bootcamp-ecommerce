"""Import a wire transfer spreadsheet"""

from django.core.management import BaseCommand

from ecommerce.api import import_wire_transfers


class Command(BaseCommand):
    """Import a CSV of wire transfer transactions"""

    help = "Import a CSV of wire transfer transactions"

    def add_arguments(self, parser):
        """Handle arguments"""
        parser.add_argument("csv_path", type=str, help="Path to the CSV")

        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            dest="force",
            help="Migrate applications even if the 'from' run and 'to' run belong to different bootcamps.",
        )

    def handle(self, *args, **options):  # noqa: ARG002
        """Import CSV of wire transfers"""
        import_wire_transfers(options["csv_path"], options["force"])
