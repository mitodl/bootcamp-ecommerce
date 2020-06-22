"""Wagtail page factories"""

import factory
from factory.django import DjangoModelFactory
import faker
import pytz
from wagtail.core.models import Site
from wagtail.core.rich_text import RichText
import wagtail_factories

from cms import models
from cms.blocks import (
    TitleLinksBlock,
    TitleDescriptionBlock,
    CatalogSectionBootcampBlock,
)
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
    title = factory.fuzzy.FuzzyText(prefix="Bootcamp: ", length=64)
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
            site = Site.objects.get(is_default_site=True)
            obj.move(site.root_page, "last-child")
            obj.refresh_from_db()
        return obj


class ResourcePageFactory(wagtail_factories.PageFactory):
    """ResourcePage factory"""

    class Meta:
        model = models.ResourcePage


class TitleLinksBlockFactory(wagtail_factories.StructBlockFactory):
    """TitleLinksBlock factory class"""

    title = factory.fuzzy.FuzzyText(prefix="title ")
    links = factory.LazyFunction(lambda: RichText("<p>{}</p>".format(FAKE.paragraph())))

    class Meta:
        model = TitleLinksBlock


class LearningResourceSectionFactory(wagtail_factories.PageFactory):
    """LearningResourceSection factory class"""

    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    items = wagtail_factories.StreamFieldFactory({"item": TitleLinksBlockFactory})

    class Meta:
        model = models.LearningResourceSection


class TitleDescriptionBlockFactory(wagtail_factories.StructBlockFactory):
    """TitleDescriptionBlock factory class"""

    title = factory.fuzzy.FuzzyText(prefix="Title ")
    description = factory.fuzzy.FuzzyText(prefix="Description ")

    class Meta:
        model = TitleDescriptionBlock


class ProgramDescriptionSectionFactory(wagtail_factories.PageFactory):
    """ProgramDescriptionSection factory class"""

    statement = factory.fuzzy.FuzzyText(prefix="statement ")
    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    body = factory.fuzzy.FuzzyText(prefix="body ")
    image = factory.SubFactory(wagtail_factories.ImageFactory)
    banner_image = factory.SubFactory(wagtail_factories.ImageFactory)
    steps = wagtail_factories.StreamFieldFactory(
        {"steps": TitleDescriptionBlockFactory}
    )

    class Meta:
        model = models.ProgramDescriptionSection


class HomePageFactory(wagtail_factories.PageFactory):
    """HomePage factory class"""

    title = factory.fuzzy.FuzzyText()
    tagline = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    slug = "wagtail-home"

    class Meta:
        model = models.HomePage

    @factory.post_generation
    def post_gen(obj, create, extracted, **kwargs):  # pylint:disable=unused-argument
        """Post-generation hook, moves home page to the root of the site"""
        if create:
            site = Site.objects.get(is_default_site=True)
            site.root_page = obj
            site.save()
        return obj


class HomeAlumniSectionFactory(wagtail_factories.PageFactory):
    """HomeAlumniSectionFactory factory class"""

    banner_image = factory.SubFactory(wagtail_factories.ImageFactory)
    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    text = factory.fuzzy.FuzzyText(prefix="text ")
    highlight_quote = factory.fuzzy.FuzzyText(prefix="quote ")
    highlight_name = highlight_quote = factory.fuzzy.FuzzyText(prefix="name ")

    class Meta:
        model = models.HomeAlumniSection


class CatalogSectionBootcampBlockFactory(wagtail_factories.StructBlockFactory):
    """CatalogSectionBootcampBlock factory class"""

    page = factory.SubFactory(BootcampRunPageFactory)
    format = factory.fuzzy.FuzzyText(prefix="format ", length=24)
    application_deadline = FAKE.date_time_this_month(before_now=False, tzinfo=pytz.utc)

    class Meta:
        model = CatalogSectionBootcampBlock


class CatalogGridSectionFactory(wagtail_factories.PageFactory):
    """CatalogGridSection factory class"""

    contents = wagtail_factories.StreamFieldFactory(
        {"bootcamp_run": CatalogSectionBootcampBlockFactory}
    )

    class Meta:
        model = models.CatalogGridSection
