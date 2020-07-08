"""Management command to change enrollment status"""
import sys

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from ecommerce.api import refund_enrollment
from ecommerce.exceptions import EcommerceException
from klasses.models import BootcampRunEnrollment
from profiles.api import fetch_user

User = get_user_model()


class Command(BaseCommand):
    """Sets a user's enrollment to 'refunded' and deactivates it"""

    help = "Sets a user's enrollment to 'refunded'"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="The id, email, or username of the enrolled User",
            required=True,
        )
        parser.add_argument(
            "--run", type=str, help="The id for an enrolled BootcampRun"
        )
        parser.add_argument("--amount", type=str, help="The amount of the refund")
        super().add_arguments(parser)

    def handle(self, *args, **options):
        """Handle command execution"""
        user = fetch_user(options["user"])
        enrollment = BootcampRunEnrollment.objects.get(
            bootcamp_run__id=options["run"], user=user
        )
        amount = Decimal(options["amount"])

        try:
            refund_enrollment(user=user, enrollment=enrollment, amount=amount)
            self.stdout.write(
                "Refunded enrollment for user: {} ({})\nEnrollment affected: {}".format(
                    user.username, user.email, enrollment.bootcamp_run.title
                )
            )
        except EcommerceException as exc:
            self.stderr.write(str(exc))
            sys.exit(1)
