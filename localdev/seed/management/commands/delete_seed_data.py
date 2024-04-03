"""Management command to delete seeded data"""

from django.core.management.base import BaseCommand

from localdev.seed.api import delete_seed_data
from localdev.seed.utils import get_raw_seed_data_from_file


class Command(BaseCommand):
    """Deletes seeded data based on raw seed data file"""

    help = __doc__

    def handle(self, *args, **options):
        raw_seed_data = get_raw_seed_data_from_file()
        results = delete_seed_data(raw_seed_data)

        if not results.has_results:
            self.stdout.write(self.style.WARNING("No results logged."))
        else:
            self.stdout.write(self.style.SUCCESS("RESULTS"))
            self.stdout.write(results.report)
