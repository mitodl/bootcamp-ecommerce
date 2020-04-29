"""
OAuth token model
"""
from django.db import models
from django.db.models import TextField, CharField, DateTimeField, IntegerField, DecimalField
from main.models import TimestampedModel
from fluidreview.constants import WebhookParseStatus
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


class WebhookRequest(TimestampedModel):
    """
    Store the webhook request from FluidReview
    """
    body = TextField(blank=True)
    status = models.CharField(
        null=False,
        default=WebhookParseStatus.CREATED,
        choices=[(status, status) for status in WebhookParseStatus.ALL_STATUSES],
        max_length=10,
    )
    # FluidReview allows invalid emails so store as a regular CharField
    user_email = CharField(null=True, blank=True, max_length=254)
    user_id = IntegerField(null=True, blank=True)
    submission_id = IntegerField(null=True, blank=True)
    award_id = IntegerField(null=True, blank=True)
    award_name = CharField(blank=True, max_length=512)
    award_cost = DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)
    amount_to_pay = DecimalField(null=True, blank=True, max_digits=20, decimal_places=2)

    class Meta:
        ordering = ['award_id', 'created_on']

    def __str__(self):
        return '<WebhookRequest created_on={} status={} >'.format(self.created_on, self.status)
