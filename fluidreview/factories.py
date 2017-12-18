"""
Factories for backend models
"""
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyInteger, FuzzyDecimal

from fluidreview import models


class OAuthTokenFactory(DjangoModelFactory):
    """Factory for OAuthToken"""
    access_token = FuzzyText()
    refresh_token = FuzzyText()

    class Meta:
        model = models.OAuthToken


class WebhookRequestFactory(DjangoModelFactory):
    """Factory for WebhookRequest"""
    body = FuzzyText()
    user_email = FuzzyText()
    user_id = FuzzyInteger(low=1)
    submission_id = FuzzyInteger(low=1)
    award_id = FuzzyInteger(low=1)
    award_name = FuzzyText()
    award_cost = FuzzyDecimal(low=0.00)
    amount_to_pay = FuzzyDecimal(low=0.00)

    class Meta:
        model = models.WebhookRequest
