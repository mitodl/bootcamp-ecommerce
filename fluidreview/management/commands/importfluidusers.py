"""
Command for importing FluidReview users
"""
import sys
from django.core.management import BaseCommand

from fluidreview import serializers
from fluidreview.api import process_user, list_users


class Command(BaseCommand):
    """
    Create user and profile objects for each FluidReview user
    """
    def handle(self, *args, **options):
        """
        Run the command
        """
        errors = False
        for fluid_user in list_users():
            serializer = serializers.UserSerializer(data=fluid_user)
            if serializer.is_valid(raise_exception=False):
                process_user(serializer.data)
                self.stdout.write('Processed User & Profile for {}'.format(fluid_user['email']))
            else:
                errors = True
                self.stdout.write('Invalid data for {}: {}'.format(fluid_user['email'], serializer.errors))
        if errors:
            sys.exit(1)
