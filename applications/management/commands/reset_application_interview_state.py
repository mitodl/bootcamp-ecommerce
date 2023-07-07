"""Management command to reset Jobma interview state for a user"""

from django.core.management.base import BaseCommand, CommandError

from applications.constants import AppStates, REVIEWABLE_APP_STATES
from applications.management.utils import fetch_bootcamp_run
from applications.models import BootcampApplication
from applications.tasks import refresh_pending_interview_links
from profiles.api import fetch_user


class Command(BaseCommand):
    """
    Reset Jobma interview based on the provided "run" and "user".
    """

    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--run",
            type=str,
            help="The id, title, or display title of the bootcamp run",
            required=True,
        )
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email, or username of the User",
            required=True,
        )

    def handle(self, *args, **options):
        user = fetch_user(options["user"])
        bootcamp_run = fetch_bootcamp_run(options["run"])

        # Ideally, there should only be one application for a user in single bootcamp run
        try:
            user_run_application = BootcampApplication.objects.get(
                user=user, bootcamp_run=bootcamp_run
            )
        except BootcampApplication.DoesNotExist:
            raise CommandError(
                f"No application found for User={user}, Run={bootcamp_run}."
            )
        if user_run_application.state not in REVIEWABLE_APP_STATES:
            raise CommandError(
                f"User's application is already in approved state. User={user}, Run={bootcamp_run}, "
                f"State={user_run_application.state}."
            )

        # Reset User's application state back to Awaiting submissions
        user_run_application.state = AppStates.AWAITING_USER_SUBMISSIONS.value
        user_run_application.save()
        refresh_pending_interview_links()

        self.stdout.write(
            self.style.SUCCESS(
                f"Jobma interview state has been reset for User={user} Run={bootcamp_run}."
            )
        )
