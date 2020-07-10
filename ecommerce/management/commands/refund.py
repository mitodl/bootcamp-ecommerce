"""Management command to change enrollment status"""
import sys

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from ecommerce.api import process_refund
from ecommerce.exceptions import EcommerceException
from klasses.models import BootcampRun
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
            "--run", type=int, help="The id for an enrolled BootcampRun", required=True
        )
        parser.add_argument(
            "--amount", type=Decimal, help="The amount of the refund", required=True
        )
        super().add_arguments(parser)

    def handle(self, *args, **options):
        """Handle command execution"""
        user = fetch_user(options["user"])
        bootcamp_run = BootcampRun.objects.get(id=options["run"])
        amount = Decimal(options["amount"])

        try:
            process_refund(user=user, bootcamp_run=bootcamp_run, amount=amount)
            self.stdout.write(
                "Refunded user: {} ({})\nBootcamp Run affected: {}\nRefund Amount: ${}".format(
                    user.username, user.email, bootcamp_run.title, amount
                )
            )
        except EcommerceException as exc:
            self.stderr.write(str(exc))
            sys.exit(1)
