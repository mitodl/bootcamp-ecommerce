"""
OAuth token model
"""
from django.db import models
from django.db.models import TextField, CharField, DateTimeField, IntegerField

from fluidreview.utils import utc_now


class OAuthToken(models.Model):
    """
    Store the OAuth access and refresh tokens for the FluidReview API,
    because it has short-lived refresh tokens (invalidated whenever used).
    """
    # There should only be one row in this table.
    id = IntegerField(unique=True, primary_key=True, null=False, default=1)
    access_token = TextField(null=True)
    refresh_token = TextField(null=True)
    token_type = CharField(max_length=30, default='Bearer')
    expires_on = DateTimeField(null=False)

    @property
    def json(self):
        """
        Return the token in an OAuth2Session-compatible format

        Returns:
            dict: Token attributes
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'token_type': self.token_type,
            'expires_in': int((self.expires_on - utc_now()).total_seconds())
        }
