"""
Management command to manage certificates.
"""

from django.core.management.base import BaseCommand, CommandError

from klasses.api import fetch_bootcamp_run
from klasses.utils import (
    generate_single_certificate,
    generate_batch_certificates,
    revoke_certificate,
    unrevoke_certificate,
    manage_user_certificate_blocking,
)
from profiles.api import fetch_user


class Command(BaseCommand):
    """
    Command to manage certificates.
    """

    help = "Creates, assigns and revokes certificates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email or username of the enrolled User",
            required=False,
        )
        parser.add_argument(
            "--run",
            type=str,
            help="The 'bootcamprun_id' value for a bootcamprun",
            required=False,
        )
        parser.add_argument(
            "--block",
            nargs="*",
            default=[],
            required=False,
            help="Flag for blocking certificate generation for provided users",
        )
        parser.add_argument(
            "--unblock",
            nargs="*",
            default=[],
            required=False,
            help="Flag for unblocking certificate generation for provided users",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--revoke",
            help="Flag to revoke single certificate",
            dest="revoke",
            action="store_true",
            required=False,
        )
        group.add_argument(
            "--unrevoke",
            help="Flag to unrevoke single certificate",
            dest="unrevoke",
            action="store_true",
            required=False,
        )
        group.add_argument(
            "--generate",
            help="Flag for single certificate generation",
            dest="generate",
            action="store_true",
            required=False,
        )
        group.add_argument(
            "--generate-batch",
            help="Flag for batch certificate generation",
            dest="generate_batch",
            action="store_true",
            required=False,
        )

        super().add_arguments(parser)

    def handle(
        self, *args, **options
    ):  # pylint: disable=too-many-locals, too-many-branches
        """Handle command execution"""
        try:
            user = fetch_user(options["user"]) if options["user"] else None
            generate_single = options.get("generate")
            generate_batch = options.get("generate_batch")
            if options.get("run"):
                bootcamp_run = fetch_bootcamp_run(str(options.get("run")))
            revoke = options.get("revoke")
            unrevoke = options.get("unrevoke")
            users_to_block = options.get("block")
            users_to_unblock = options.get("unblock")
        except:
            raise CommandError("Provided values are not valid.")

        if generate_single and (not user or not bootcamp_run):
            raise CommandError(
                "A valid 'user' and 'run' must be provided with 'generate'."
            )
        if generate_batch and not bootcamp_run:
            raise CommandError("A valid 'run' must be provided with 'generate-batch'.")
        if (revoke or unrevoke) and (not user or not bootcamp_run):
            raise CommandError(
                "A valid 'user' and 'run' must be provided with 'revoke' or 'unrevoke'"
            )
        if (users_to_block or users_to_unblock) and not options.get("run"):
            raise CommandError(
                "A valid 'run' must be provided along with 'block or unblock'."
            )

        if users_to_block:
            result = manage_user_certificate_blocking(
                users_to_block, True, bootcamp_run
            )
            self.show_message(**result)
        elif users_to_unblock:
            result = manage_user_certificate_blocking(
                users_to_unblock, False, bootcamp_run
            )
            self.show_message(**result)
        elif revoke and user and bootcamp_run:
            result = revoke_certificate(user, bootcamp_run)
            self.show_message(**result)
        elif unrevoke and user and bootcamp_run:
            result = unrevoke_certificate(user, bootcamp_run)
            self.show_message(**result)
        elif generate_single and bootcamp_run and user:
            result = generate_single_certificate(user, bootcamp_run)
            self.show_message(**result)
        elif generate_batch and bootcamp_run:
            result = generate_batch_certificates(bootcamp_run)
            self.show_message(**result)
        else:
            raise CommandError(
                "Provided values are not enough to govern any process, kidnly use --help for more details"
            )

    def show_message(self, updated, msg):
        """Displays messages on console"""
        self.stdout.write(
            self.style.SUCCESS(msg)
            if updated
            else self.style.WARNING("No changes were made.\n{}".format(msg))
        )
