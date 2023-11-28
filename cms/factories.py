"""Wagtail page factories"""

import factory
from factory.django import DjangoModelFactory
import faker
import pytz
from wagtail.models import Site
from wagtail.rich_text import RichText
import wagtail_factories

from cms import models
from cms.blocks import (
    TitleLinksBlock,
    TitleDescriptionBlock,
    CatalogSectionBootcampBlock,
    ThreeColumnImageTextBlock,
    InstructorSectionBlock,
    InstructorBlock,
    SponsorSectionBlock,
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
    parent = factory.SubFactory(wagtail_factories.PageFactory)

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


class BootcampIndexPageFactory(wagtail_factories.PageFactory):
    """Factory for BootcampIndexPage"""

    title = factory.Faker("text", max_nb_chars=15)

    class Meta:
        model = models.BootcampIndexPage


class ResourcePageFactory(wagtail_factories.PageFactory):
    """ResourcePage factory"""

    header_image = factory.SubFactory(wagtail_factories.ImageFactory)

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


class ThreeColumnImageTextBlockFactory(wagtail_factories.StructBlockFactory):
    """ThreeColumnImageTextBlockFactory factory class"""

    heading = factory.fuzzy.FuzzyText(prefix="Heading ")
    sub_heading = factory.fuzzy.FuzzyText(prefix="Sub Heading ")
    body = factory.LazyFunction(lambda: RichText("<p>{}</p>".format(FAKE.paragraph())))
    image = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = ThreeColumnImageTextBlock


class InstructorBlockFactory(wagtail_factories.StructBlockFactory):
    """InstructorBlockFactory factory class"""

    name = factory.fuzzy.FuzzyText(prefix="Name ")
    image = factory.SubFactory(wagtail_factories.ImageFactory)
    title = factory.fuzzy.FuzzyText(prefix="Title ")

    class Meta:
        model = InstructorBlock


class InstructorSectionBlockFactory(wagtail_factories.StructBlockFactory):
    """InstructorSectionBlockFactory factory class"""

    heading = factory.fuzzy.FuzzyText(prefix="Heading ")
    sub_heading = factory.fuzzy.FuzzyText(prefix="Sub Heading ")
    heading_singular = factory.fuzzy.FuzzyText(prefix="Heading Singular ")
    members = factory.SubFactory(InstructorBlockFactory)

    class Meta:
        model = InstructorSectionBlock


class SponsorSectionBlockFactory(wagtail_factories.StructBlockFactory):
    """SponsorSectionBlockFactory factory class"""

    heading = factory.fuzzy.FuzzyText(prefix="Heading ")
    sub_heading = factory.fuzzy.FuzzyText(prefix="Sub Heading ")
    heading_singular = factory.fuzzy.FuzzyText(prefix="Heading Singular ")
    sponsors = factory.SubFactory(InstructorBlockFactory)

    class Meta:
        model = SponsorSectionBlock


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


class ThreeColumnImageTextSectionFactory(wagtail_factories.PageFactory):
    """ThreeColumnImageTextSection factory class"""

    column_image_text_section = wagtail_factories.StreamFieldFactory(
        {"column_image_text_section": ThreeColumnImageTextBlockFactory}
    )

    class Meta:
        model = models.ThreeColumnImageTextSection


class HomePageFactory(wagtail_factories.PageFactory):
    """HomePage factory class"""

    title = factory.fuzzy.FuzzyText()
    tagline = factory.fuzzy.FuzzyText()
    description = factory.fuzzy.FuzzyText()
    parent = factory.SubFactory(wagtail_factories.PageFactory)
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


class LetterTemplatePageFactory(wagtail_factories.PageFactory):
    """Factory class for the LetterTemplatePage"""

    signatory_name = factory.fuzzy.FuzzyText(prefix="Test ")
    signature_image = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = models.LetterTemplatePage


class ResourcePagesSettingsFactory(DjangoModelFactory):
    """Factory for ResourcePagesSettings"""

    site = factory.SubFactory(wagtail_factories.SiteFactory, is_default_site=True)

    apply_page = factory.SubFactory(ResourcePageFactory, title="Apply")
    about_us_page = factory.SubFactory(ResourcePageFactory, title="About Us")
    bootcamps_programs_page = factory.SubFactory(
        ResourcePageFactory, title="Bootcamps Programs"
    )
    terms_of_service_page = factory.SubFactory(
        ResourcePageFactory, title="Terms of Service"
    )
    privacy_policy_page = factory.SubFactory(
        ResourcePageFactory, title="Privacy Policy"
    )

    class Meta:
        model = models.ResourcePagesSettings


class InstructorSectionFactory(wagtail_factories.PageFactory):
    """InstructorSectionFactory factory class"""

    banner_image = factory.SubFactory(wagtail_factories.ImageFactory)
    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    sections = wagtail_factories.StreamFieldFactory(
        {"section": InstructorSectionBlockFactory}
    )

    class Meta:
        model = models.InstructorsSection


class SponsorSectionFactory(wagtail_factories.PageFactory):
    """SponsorSectionFactory factory class"""

    banner_image = factory.SubFactory(wagtail_factories.ImageFactory)
    heading = factory.fuzzy.FuzzyText(prefix="heading ")
    sections = wagtail_factories.StreamFieldFactory(
        {"section": InstructorSectionBlockFactory}
    )

    class Meta:
        model = models.SponsorsSection


class AdmissionSectionFactory(wagtail_factories.PageFactory):
    """AdmissionSectionFactory factory class"""

    admissions_image = factory.SubFactory(wagtail_factories.ImageFactory)
    notes = factory.fuzzy.FuzzyText(prefix="heading ")
    details = factory.LazyFunction(
        lambda: RichText("<p>{}</p>".format(FAKE.paragraph()))
    )
    bootcamp_location = factory.fuzzy.FuzzyText(prefix="heading ")
    bootcamp_location_details = factory.LazyFunction(
        lambda: RichText("<p>{}</p>".format(FAKE.paragraph()))
    )
    dates = factory.fuzzy.FuzzyText(prefix="heading ")
    dates_details = factory.LazyFunction(
        lambda: RichText("<p>{}</p>".format(FAKE.paragraph()))
    )
    price = factory.fuzzy.FuzzyInteger(10)
    price_details = factory.LazyFunction(
        lambda: RichText("<p>{}</p>".format(FAKE.paragraph()))
    )

    class Meta:
        model = models.AdmissionsSection


class SignatoryPageFactory(wagtail_factories.PageFactory):
    """SignatoryPage factory class"""

    name = factory.fuzzy.FuzzyText(prefix="Name")
    title_1 = factory.fuzzy.FuzzyText(prefix="Title_1")
    title_2 = factory.fuzzy.FuzzyText(prefix="Title_2")
    organization = factory.fuzzy.FuzzyText(prefix="Organization")
    signature_image = factory.SubFactory(wagtail_factories.ImageFactory)

    class Meta:
        model = models.SignatoryPage


class CertificateIndexPageFactory(wagtail_factories.PageFactory):
    """CertificateIndexPage factory class"""

    slug = factory.fuzzy.FuzzyText()

    class Meta:
        model = models.CertificateIndexPage


class CertificatePageFactory(wagtail_factories.PageFactory):
    """CertificatePage factory class"""

    bootcamp_run_name = factory.fuzzy.FuzzyText(prefix="bootcamp_run_")
    certificate_name = factory.fuzzy.FuzzyText()
    location = factory.fuzzy.FuzzyText()
    signatories = wagtail_factories.StreamFieldFactory(
        {"signatory": SignatoryPageFactory}
    )

    class Meta:
        model = models.CertificatePage
