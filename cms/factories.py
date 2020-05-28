"""Wagtail page factories"""

import factory
from factory import SubFactory
from factory.django import DjangoModelFactory
import wagtail_factories
from wagtail.core.models import Page

from cms import models
from klasses.factories import BootcampRunFactory


class SiteNotificationFactory(DjangoModelFactory):
    """SiteNotification factory class"""

    message = factory.fuzzy.FuzzyText(prefix="message ")

    class Meta:
        model = models.SiteNotification


class BootcampRunPageFactory(wagtail_factories.PageFactory):
    """BootcampRunPage factory class"""

    bootcamp_run = SubFactory(BootcampRunFactory)
    description = factory.fuzzy.FuzzyText()
    subhead = factory.fuzzy.FuzzyText(prefix="Sub-heading - ")
    header_image = factory.SubFactory(wagtail_factories.ImageFactory)
    thumbnail_image = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = models.BootcampRunPage

    @factory.post_generation
    def post_gen(obj, create, extracted, **kwargs):  # pylint:disable=unused-argument
        """Post-generation hook"""
        if create:
            # Move the created page to be a child of the home page
            home_page = Page.objects.get(depth=2)
            obj.move(home_page, "last-child")
            obj.refresh_from_db()
        return obj
