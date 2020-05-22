"""Wagtail page factories"""

import factory
from factory.django import DjangoModelFactory

from cms.models import SiteNotification


class SiteNotificationFactory(DjangoModelFactory):
    """SiteNotification factory class"""

    message = factory.fuzzy.FuzzyText(prefix="message ")

    class Meta:
        model = SiteNotification
