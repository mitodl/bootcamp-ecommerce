"""
Retire user from BootCamp
"""

import logging
from argparse import RawTextHelpFormatter
from urllib.parse import urlparse

from django.conf import settings
from django.core.management import BaseCommand, CommandError
from social_django.models import UserSocialAuth

from user_util import user_util
from jobma.constants import EXPIRED
from jobma.models import Interview
from profiles.api import fetch_users

log = logging.getLogger(__name__)


RETIRED_USER_SALTS = ["bootcamp-retired-email"]
RETIRED_EMAIL_FMT = "retired_email_{}@retired." + "{}".format(
    urlparse(settings.SITE_BASE_URL).netloc
)


class Command(BaseCommand):
    """
    Retire user from BootCamp
    """

    help = """
Retire one or multiple users. Username or email can be used to identify a user.

For single user use:\n
`./manage.py retire_users --user=foo` or do \n
`./manage.py retire_users -u foo` or do \n
`./manage.py retire_users -u foo@email.com` \n

For multiple users, add arg `--user` for each user i.e:\n
`./manage.py retire_users --user=foo --user=bar --user=baz` or do \n
`./manage.py retire_users --user=foo@email.com --user=bar@email.com --user=baz` or do \n
`./manage.py retire_users -u foo -u bar -u baz`
"""

    def create_parser(self, prog_name, subcommand, **kwargs):
        """
        create parser to add new line in help text.
        """
        parser = super(Command, self).create_parser(prog_name, subcommand)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        """create args"""
        # pylint: disable=expression-not-assigned
        parser.add_argument(
            "-u",
            "--user",
            action="append",
            default=[],
            dest="users",
            help="Single or multiple user name",
        )

    def get_retired_email(self, email):
        """Convert user email to retired email format."""
        return user_util.get_retired_email(email, RETIRED_USER_SALTS, RETIRED_EMAIL_FMT)

    def display_messages(self, message, log_messages, is_error=False):
        """
        Display error on console
        Args:
            message (str): message to display
            is_error (bool): is error for styling
            log_messages (list): Accumulated message
        """
        self.stdout.write(message, style_func=self.style.ERROR if is_error else None)
        log_messages.append(message)

    def handle(self, *args, **kwargs):  # pylint: disable=unused-argument
        users = kwargs.get("users", [])
        if not users:
            # show error when no user selected.
            raise CommandError(
                "No user(s) provided. Please provide user(s) using -u or --user."
            )

        users = fetch_users(kwargs["users"])
        for user in users:
            log_messages = []

            # retire user
            self.display_messages(f"Retiring user {user}", log_messages)

            if not user.is_active:
                self.stdout.write(
                    self.style.ERROR(
                        "User: '{user}' is already deactivated in MIT BootCamp".format(
                            user=user
                        )
                    )
                )
                continue

            # mark user inactive
            user.is_active = False

            # Change user password & email
            email = user.email
            user.email = self.get_retired_email(user.email)
            user.set_unusable_password()
            user.save()

            self.display_messages(
                f"Email changed from '{email}' to '{user.email}' and password is not useable now",
                log_messages,
            )

            # reset user social
            auth_delete_count, _ = UserSocialAuth.objects.filter(user=user).delete()
            self.display_messages(
                f"For user {user}: {auth_delete_count} SocialAuth rows deleted",
                log_messages,
            )

            Interview.objects.filter(applicant=user).update(status=EXPIRED)
            self.display_messages(
                f"For user {user}: Interview statuses are expired now.", log_messages
            )

            # finish
            self.display_messages(f"User '{user}' is retired", log_messages)
            log.info("\n".join(log_messages[1:]))
