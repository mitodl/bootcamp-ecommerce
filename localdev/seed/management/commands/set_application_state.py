"""Management command to manipulate a bootcamp application into a certain state"""

from django.core.management.base import BaseCommand, CommandError

from applications.models import BootcampApplication
from klasses.api import fetch_bootcamp_run
from localdev.seed.app_state_api import ALLOWED_STATES, set_application_state
from profiles.api import fetch_user


class Command(BaseCommand):
    """Manipulate a bootcamp application into a certain state"""

    help = __doc__

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email, or username of the User",
            required=False,
        )
        parser.add_argument(
            "--run",
            type=str,
            help="The id, title, or display title of the bootcamp run",
            required=False,
        )
        parser.add_argument(
            "--app-id",
            "-i",
            type=int,
            help="The bootcamp application id",
            required=False,
        )
        parser.add_argument(
            "--state",
            "-s",
            type=str,
            choices=ALLOWED_STATES,
            help="The target state of the application",
            required=True,
        )

    def handle(self, *args, **options):  # noqa: ARG002, D102
        if not options["app_id"] and not (options["user"] and options["run"]):
            raise CommandError(
                "Need to provide the bootcamp application id, or both the user and bootcamp run."  # noqa: EM101
            )
        app_filters = {}
        if options["app_id"]:
            app_filters["id"] = options["app_id"]
        else:
            user = fetch_user(options["user"])
            run = fetch_bootcamp_run(options["run"])
            app_filters.update({"user": user, "bootcamp_run": run})
        bootcamp_app = BootcampApplication.objects.get(**app_filters)
        prev_state = bootcamp_app.state
        bootcamp_app = set_application_state(
            bootcamp_app, target_state=options["state"]
        )
        self.stdout.write(self.style.SUCCESS("Application: "))
        self.stdout.write(str(bootcamp_app))
        self.stdout.write(
            self.style.SUCCESS(f"State change: {prev_state} -> {bootcamp_app.state}")
        )
