"""Management command to change enrollment status"""
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.management.base import CommandError
from django.contrib.auth import get_user_model

from klasses.api import defer_enrollment
from klasses.management.utils import EnrollmentChangeCommand, enrollment_summary
from klasses.models import BootcampRun, BootcampRunEnrollment
from profiles.api import fetch_user

User = get_user_model()


class Command(EnrollmentChangeCommand):
    """Sets a user's enrollment to 'deferred' and creates an enrollment for a different bootcamp run"""

    help = "Sets a user's enrollment to 'deferred' and creates an enrollment for a different bootcamp run"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email, or username of the enrolled User",
            required=True,
        )
        parser.add_argument(
            "--from-run",
            type=str,
            help="The 'bootcamp_run_id' value for an enrolled BootcampRun",
            required=True,
        )
        parser.add_argument(
            "--to-run",
            type=str,
            help="The 'bootcamp_run_id' value for the BootcampRun that you are deferring to",
            required=True,
        )
        parser.add_argument(
            "--order",
            type=int,
            help="The 'order_id' value for an user's order ID",
            required=True,
        )
        super().add_arguments(parser)

    def handle(self, *args, **options):
        """Handle command execution"""
        user = fetch_user(options["user"])
        from_bootcamp_run_id = options["from_run"]
        to_bootcamp_run_id = options["to_run"]
        order = options["order"]
        force = options["force"]

        try:
            from_enrollment, to_enrollment = defer_enrollment(
                user, from_bootcamp_run_id, to_bootcamp_run_id, order, force
            )
        except ObjectDoesNotExist as exc:
            if isinstance(exc, BootcampRunEnrollment.DoesNotExist):
                message = "'from' bootcamp run enrollment does not exist ({})".format(
                    to_bootcamp_run_id
                )
            elif isinstance(exc, BootcampRun.DoesNotExist):
                message = "'to' bootcamp does not exist ({})".format(to_bootcamp_run_id)
            else:
                message = str(exc)
            raise CommandError(message)
        except ValidationError as exc:
            raise CommandError("Invalid enrollment deferral - {}".format(exc))
        else:
            if not to_enrollment:
                raise CommandError(
                    "Failed to create/update the target enrollment ({})".format(
                        to_bootcamp_run_id
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Deferred enrollment for user: {}\n"
                "Enrollment deactivated: {}\n"
                "Enrollment created/updated: {}".format(
                    user,
                    enrollment_summary(from_enrollment),
                    enrollment_summary(to_enrollment),
                )
            )
        )
