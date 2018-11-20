"""
Factories for backend models
"""
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText, FuzzyInteger

from smapply import models


class OAuthTokenSMAFactory(DjangoModelFactory):
    """Factory for OAuthTokenSMA"""
    access_token = FuzzyText()
    refresh_token = FuzzyText()

    class Meta:
        model = models.OAuthTokenSMA


class WebhookRequestSMAFactory(DjangoModelFactory):
    """Factory for WebhookRequestSMA"""
    body = FuzzyText()
    user_id = FuzzyInteger(low=1)
    submission_id = FuzzyInteger(low=1)
    award_id = FuzzyInteger(low=1)
    award_title = FuzzyText()

    class Meta:
        model = models.WebhookRequestSMA
