"""Wagtail page factories"""

import factory
from factory.django import DjangoModelFactory
import faker
from wagtail.core.models import Page
from wagtail.core.rich_text import RichText
import wagtail_factories

from cms import models
from cms.blocks import TitleLinksBlock
from klasses.factories import BootcampRunFactory


FAKE = faker.Factory.create()


class SiteNotificationFactory(DjangoModelFactory):
    """SiteNotification factory class"""

    message = factory.fuzzy.FuzzyText(prefix="message ")

    class Meta:
        model = models.SiteNotification


class BootcampRunPageFactory(wagtail_factories.PageFactory):
    """BootcampRunPage factory class"""

    bootcamp_run = factory.SubFactory(BootcampRunFactory)
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


class TitleLinksBlockFactory(wagtail_factories.StructBlockFactory):
    """TitleLinksBlock factory class"""

    title = factory.fuzzy.FuzzyText(prefix="title ")
    links = factory.LazyFunction(lambda: RichText("<p>{}</p>".format(FAKE.paragraph())))

    class Meta:
        model = TitleLinksBlock


class LearningResourcePageFactory(wagtail_factories.PageFactory):
    """LearningResourcePage factory class"""

    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    items = wagtail_factories.StreamFieldFactory({"item": TitleLinksBlockFactory})

    class Meta:
        model = models.LearningResourcePage
