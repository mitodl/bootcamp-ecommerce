"""Management command to correctly set the state of a bootcamp application"""
from django.core.management.base import BaseCommand

from applications.api import derive_application_state
from applications.models import BootcampApplication
from klasses.models import BootcampRun
from profiles.api import fetch_user


class Command(BaseCommand):
    """Correctly set the state of a bootcamp application"""

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email, or username of the User",
            required=True,
        )
        parser.add_argument(
            "--run",
            type=str,
            help="The id or title of the bootcamp run",
            required=True,
        )

    def handle(self, *args, **options):
        user = fetch_user(options["user"])
        run_property = options["run"]
        if run_property.isdigit():
            bootcamp_run = BootcampRun.objects.get(id=run_property)
        else:
            bootcamp_run = BootcampRun.objects.get(title=run_property)
        bootcamp_app = BootcampApplication.objects.get(user=user, bootcamp_run=bootcamp_run)
        derived_state = derive_application_state(bootcamp_app)

        if bootcamp_app.state != derived_state:
            previous_state = bootcamp_app.state
            bootcamp_app.state = derived_state
            bootcamp_app.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Bootcamp application state changed ({previous_state} -> {bootcamp_app.state})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Bootcamp application state unchanged ({bootcamp_app.state})"
                )
            )
