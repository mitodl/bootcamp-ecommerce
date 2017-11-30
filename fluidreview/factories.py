"""
Factories for backend models
"""
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from fluidreview import models


class OAuthTokenFactory(DjangoModelFactory):
    """Factory for OAuthToken"""
    access_token = FuzzyText()
    refresh_token = FuzzyText()

    class Meta:
        model = models.OAuthToken
