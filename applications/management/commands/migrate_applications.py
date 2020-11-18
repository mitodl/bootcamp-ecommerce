"""Management command to create applications for users that already applied to another bootcamp run"""
from django.core.management.base import BaseCommand, CommandError

from applications.constants import APPROVED_APP_STATES
from applications.management.utils import (
    fetch_bootcamp_run,
    migrate_application,
    has_same_application_steps,
)
from applications.models import BootcampApplication
from profiles.api import fetch_user


class Command(BaseCommand):
    """Create applications for users that already applied to another bootcamp run"""

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--from-run",
            type=str,
            help="The id or title of the bootcamp run that users have already applied to.",
            required=True,
        )
        parser.add_argument(
            "--to-run",
            type=str,
            help="The id or title of the bootcamp run for which new applications should be created.",
            required=True,
        )
        parser.add_argument(
            "--users",
            type=str,
            help=(
                "(Optional) Comma-separated list of user ids, emails, or usernames. "
                "This will limit the users that are migrated."
            ),
            required=False,
        )
        parser.add_argument(
            "--skip-confirm",
            action="store_true",
            help="Migrate applications without waiting for user confirmation.",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            dest="force",
            help="Migrate applications even if the 'from' run and 'to' run belong to different bootcamps.",
        )

    def handle(self, *args, **options):  # pylint: disable=too-many-locals
        from_run_property = options["from_run"]
        to_run_property = options["to_run"]
        from_run = fetch_bootcamp_run(from_run_property)
        to_run = fetch_bootcamp_run(to_run_property)
        users_property = options["users"]
        users = (
            None
            if not users_property
            else [
                fetch_user(user_property) for user_property in users_property.split(",")
            ]
        )
        application_filter = dict(bootcamp_run=from_run, state__in=APPROVED_APP_STATES)
        if users:
            application_filter["user__in"] = users
        from_run_applications = BootcampApplication.objects.filter(**application_filter)

        if not from_run_applications.exists():
            raise CommandError(
                f"No completed applications found with the given filters:\n{application_filter}"
            )
        if from_run.bootcamp != to_run.bootcamp and options["force"] is False:
            raise CommandError(
                "'from' run and 'to' run are from different bootcamps "
                f"('{from_run.bootcamp.title}', '{to_run.bootcamp.title}').\n"
                "Use '--force' flag to migrate anyway."
            )
        if from_run.bootcamp != to_run.bootcamp and not has_same_application_steps(
            from_run.bootcamp.id, to_run.bootcamp.id
        ):
            raise CommandError(
                f"The 'from' run and 'to' run have different application steps for their respective bootcamps "
                f"('{from_run.bootcamp.title}', '{to_run.bootcamp.title}')."
            )

        if not options["skip_confirm"]:
            user_input = input(
                f"{len(from_run_applications)} application(s) will be migrated to '{to_run.title}'.\n"
                "Enter 'y' to confirm, 'l' to list the users that will be affected, or any other key to exit: "
            )
            user_input_lower = user_input.lower()
            if user_input_lower not in {"y", "l"}:
                return
            if user_input_lower == "l":
                self.stdout.write(
                    "\n".join([app.user.email for app in from_run_applications])
                )
                return

        # Migrate applications and report on results
        migrated_applications = []
        for from_run_application in from_run_applications:
            try:
                to_run_application = migrate_application(from_run_application, to_run)
            except Exception as exc:  # pylint: disable=broad-except
                self.stdout.write(
                    self.style.ERROR(
                        "Failed to migrate user application to new run "
                        f"({from_run_application.user.email}, '{to_run.title}')."
                    )
                )
                self.stdout.write(str(exc))
            else:
                migrated_applications.append(to_run_application)

        if migrated_applications:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{len(migrated_applications)} application(s) successfully migrated to '{to_run.title}'"
                )
            )
