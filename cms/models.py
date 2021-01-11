# pylint: disable=too-many-lines
"""
Page models for the CMS
"""
from datetime import datetime
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.http.response import Http404
from django.urls import reverse
from django.utils.text import slugify
from django.shortcuts import render
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, PageChooserPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.blocks import StreamBlock, PageChooserBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.utils import WAGTAIL_APPEND_SLASH
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet

from cms.api import render_template
from cms.blocks import (
    ResourceBlock,
    InstructorSectionBlock,
    ThreeColumnImageTextBlock,
    AlumniBlock,
    TitleLinksBlock,
    TitleDescriptionBlock,
    CatalogSectionBootcampBlock,
)
from cms.constants import (
    ACCEPTANCE_DEFAULT_LETTER_TEXT,
    BOOTCAMP_INDEX_SLUG,
    CERTIFICATE_INDEX_SLUG,
    REJECTION_DEFAULT_LETTER_TEXT,
    SAMPLE_DECISION_TEMPLATE_CONTEXT,
    SIGNATORY_INDEX_SLUG,
)
from cms.forms import LetterTemplatePageForm
from klasses.models import BootcampRunCertificate


log = logging.getLogger(__name__)


class BootcampIndexPage(Page):
    """
    A placeholder class to group bootcamp run object pages as children.
    This class logically acts as no more than a "folder" to organize
    pages and add parent slug segment to the page url.
    """

    slug = BOOTCAMP_INDEX_SLUG

    parent_page_types = ["HomePage"]
    subpage_types = ["BootcampRunPage"]

    @classmethod
    def can_create_at(cls, parent):
        """
        You can only create one of this page under the home page.
        The parent is limited via the `parent_page_type` list.
        """
        return (
            super().can_create_at(parent)
            and not parent.get_children().type(cls).exists()
        )

    def route(
        self, request, path_components
    ):  # pylint:disable=useless-super-delegation
        """Placeholder to implement custom routing later on (based on some sort of courseware key like in xPRO)"""
        return super().route(request, path_components)

    def serve(self, request, *args, **kwargs):
        """
        For index page we raise a 404 because this page do not have a template
        of their own and we do not expect a page to available at their slug.
        """
        raise Http404


class CommonProperties:
    """
    This defines some common properties that are common in product and home pages.
    """

    def _get_child_page_of_type(self, cls):
        """Gets the first child page of the given type if it exists"""
        child = self.get_children().type(cls).live().first()
        return child.specific if child else None

    @property
    def program_description_section(self):
        """Gets the program description page"""
        return self._get_child_page_of_type(ProgramDescriptionSection)

    @property
    def three_column_image_text_section(self):
        """Gets the three column image text section child page"""
        return self._get_child_page_of_type(ThreeColumnImageTextSection)

    @property
    def learning_resources(self):
        """Get the learning resources page"""
        return self._get_child_page_of_type(LearningResourceSection)


class HomePage(Page, CommonProperties):
    """
    CMS page representing the website home page
    """

    template = "home_page.html"

    tagline = models.CharField(
        max_length=255,
        help_text="The tagline to display in the hero section on the page.",
    )
    description = RichTextField(
        blank=True, help_text="The description shown in the hero section on the page."
    )

    content_panels = Page.content_panels + [
        FieldPanel("tagline"),
        FieldPanel("description"),
    ]

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "CSOURCE_PAYLOAD": None,
            "site_name": settings.SITE_NAME,
            "title": self.title,
            # properties
            "alumni": self.alumni,
            "catalog": self.catalog,
            "learning_resources": self.learning_resources,
            "program_description_section": self.program_description_section,
            "three_column_image_text_section": self.three_column_image_text_section,
        }

    @property
    def alumni(self):
        """Gets the alumni section page"""
        return self._get_child_page_of_type(HomeAlumniSection)

    @property
    def catalog(self):
        """Gets the catalog section page"""
        return self._get_child_page_of_type(CatalogGridSection)

    subpage_types = [
        "ProgramDescriptionSection",
        "ThreeColumnImageTextSection",
        "HomeAlumniSection",
        "BootcampIndexPage",
        "LearningResourceSection",
        "ResourcePage",
        "CatalogGridSection",
        "LetterTemplatePage",
        "SignatoryIndexPage",
        "CertificateIndexPage",
    ]


class BootcampPage(Page, CommonProperties):
    """
    CMS page representing a Bootcamp Page
    """

    class Meta:
        abstract = True

    description = RichTextField(
        blank=True, help_text="The description shown on the page."
    )
    subhead = models.CharField(
        max_length=255,
        help_text="The subhead to display in the header section on the page.",
    )
    header_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Header image size must be at least 1900x650 pixels.",
    )
    thumbnail_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Thumbnail size must be at least 690x530 pixels.",
    )
    content_panels = [
        FieldPanel("title", classname="full"),
        FieldPanel("subhead", classname="full"),
        FieldPanel("description", classname="full"),
        ImageChooserPanel("header_image"),
        ImageChooserPanel("thumbnail_image"),
    ]

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "site_name": settings.SITE_NAME,
            "title": self.title,
            "apply_url": reverse("applications"),
            "CSOURCE_PAYLOAD": None,
        }

    @property
    def instructors(self):
        """Gets the faculty members page"""
        return self._get_child_page_of_type(InstructorsSection)

    @property
    def alumni(self):
        """Gets the faculty members page"""
        return self._get_child_page_of_type(AlumniSection)

    @property
    def certificate_page(self):
        """Gets the certificate child page"""
        return self._get_child_page_of_type(CertificatePage)

    @property
    def admissions_section(self):
        """Gets the admissions section child page"""
        return self._get_child_page_of_type(AdmissionsSection)

    subpage_types = [
        "ThreeColumnImageTextSection",
        "ProgramDescriptionSection",
        "InstructorsSection",
        "AlumniSection",
        "LearningResourceSection",
        "AdmissionsSection",
        "CertificatePage",
    ]


class BootcampRunPage(BootcampPage):
    """
    CMS page representing a bootcamp run
    """

    parent_page_types = ["BootcampIndexPage"]
    template = "product_page.html"

    bootcamp_run = models.OneToOneField(
        "klasses.BootcampRun",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The bootcamp run for this page",
    )

    def copy(self, *args, **kwargs):  # pylint: disable=signature-differs
        kwargs["copy_revisions"] = False
        kwargs["exclude_fields"] = kwargs.get("exclude_fields", []) + ["bootcamp_run"]
        kwargs["keep_live"] = False
        return super().copy(*args, **kwargs)

    content_panels = [FieldPanel("bootcamp_run")] + BootcampPage.content_panels

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            # properties
            "admissions_section": self.admissions_section,
            "alumni": self.alumni,
            "instructors": self.instructors,
            "learning_resources": self.learning_resources,
            "program_description_section": self.program_description_section,
            "three_column_image_text_section": self.three_column_image_text_section,
        }


class BootcampRunChildPage(Page):
    """
    Abstract page representing a child of BootcampRun Page
    """

    class Meta:
        abstract = True

    parent_page_types = ["BootcampRunPage", "HomePage"]

    # disable promote panels, no need for slug entry, it will be autogenerated
    promote_panels = []

    def parent(self):
        """Gets the parent page"""
        return self.get_parent().specific if self.get_parent() else None

    @classmethod
    def can_create_at(cls, parent):
        # You can only create one of these page under bootcamp.
        return (
            super().can_create_at(parent)
            and parent.get_children().type(cls).count() == 0
        )

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        # autogenerate a unique slug so we don't hit a ValidationError
        if not self.title:
            self.title = self.__class__._meta.verbose_name.title()
        self.slug = slugify("{}-{}".format(self.title, self.id))
        super().save(*args, **kwargs)

    def get_url_parts(self, request=None):
        """
        Override how the url is generated for bootcamp run child pages
        """
        # Verify the page is routable
        url_parts = super().get_url_parts(request=request)

        if not url_parts:
            return None

        site_id, site_root, parent_path = self.get_parent().specific.get_url_parts(
            request=request
        )
        page_path = ""

        # Depending on whether we have trailing slashes or not, build the correct path
        if WAGTAIL_APPEND_SLASH:
            page_path = "{}{}/".format(parent_path, self.slug)
        else:
            page_path = "{}/{}".format(parent_path, self.slug)
        return (site_id, site_root, page_path)

    def serve(self, request, *args, **kwargs):
        """
        As the name suggests these pages are going to be children of some other page. They are not
        designed to be viewed on their own so we raise a 404 if someone tries to access their slug.
        """
        raise Http404


class ThreeColumnImageTextSection(BootcampRunChildPage):
    """
    Represents a three column section along with images on the top (in each column) and text fields.
    Have a limit of maximum and minimum of three blocks.
    """

    column_image_text_section = StreamField(
        StreamBlock(
            [("column_image_text_section", ThreeColumnImageTextBlock())],
            min_num=3,
            max_num=3,
        ),
        blank=False,
        null=True,
        help_text="Enter detail about area upto max 3 blocks.",
    )

    content_panels = [StreamFieldPanel("column_image_text_section")]


class ProgramDescriptionSection(BootcampRunChildPage):
    """
    Describe the bootcamp program.
    """

    statement = RichTextField(
        blank=True,
        help_text="The bold statement for the bootcamp program in product page.",
    )
    heading = models.CharField(
        max_length=255,
        default="Program Description",
        help_text="The heading to display in the header section on the page.",
    )
    body = RichTextField(
        help_text="The body text to display in the header section on the page."
    )
    banner_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This image will be rendered in program-description section of home page.",
    )
    image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image that will render in the program description section.",
    )

    steps = StreamField(
        StreamBlock([("steps", TitleDescriptionBlock())], min_num=1, max_num=7),
        blank=False,
        null=True,
        help_text="Enter detail about steps upto max 7 steps.",
    )

    content_panels = [
        FieldPanel("statement", classname="full"),
        FieldPanel("heading", classname="full"),
        FieldPanel("body", classname="full"),
        ImageChooserPanel("image"),
        ImageChooserPanel("banner_image"),
        StreamFieldPanel("steps"),
    ]


class InstructorsSection(BootcampRunChildPage):
    """
    InstructorsPage representing a "Your MIT Instructors" section on a product page
    """

    banner_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that will display as a banner at the top of the section, must be at least 750x505 pixels.",
    )
    heading = RichTextField(
        default="Instructors",
        blank=False,
        help_text="The heading to display on this section.",
    )
    sections = StreamField(
        [("section", InstructorSectionBlock())],
        help_text="The instructor to display in this section",
    )
    content_panels = [
        ImageChooserPanel("banner_image"),
        FieldPanel("heading"),
        StreamFieldPanel("sections"),
    ]


class AdmissionsSection(BootcampRunChildPage):
    """
    Page that represents the admissions section on a bootcamp run page
    """

    admissions_image = models.ForeignKey(
        Image,
        on_delete=models.PROTECT,
        related_name="+",
        help_text="Image to show at the top of this section, size must be at least 1900x650 pixels.",
    )
    notes = models.CharField(
        max_length=255, help_text="Any notes to display, e.g. application deadline etc."
    )
    details = RichTextField(help_text="Admission details that need to be displayed.")
    bootcamp_format = models.CharField(
        max_length=255, help_text="Format of the bootcamp, e.g. Online Bootcamp"
    )
    bootcamp_format_details = RichTextField(
        blank=True, help_text="Details of the format"
    )
    dates = models.CharField(
        max_length=255,
        help_text="The start/end dates to display for this bootcamp run, e.g. April 17 - June 23, 2020",
    )
    dates_details = RichTextField(
        blank=True, help_text="Any details to show for the bootcamp dates."
    )
    price = models.IntegerField(
        help_text="The price to display for this bootcamp, e.g. 100"
    )
    price_details = RichTextField(
        blank=True, help_text="Price details to display if any."
    )

    content_panels = [
        ImageChooserPanel("admissions_image"),
        FieldPanel("notes"),
        FieldPanel("details"),
        FieldPanel("bootcamp_format"),
        FieldPanel("bootcamp_format_details"),
        FieldPanel("dates"),
        FieldPanel("dates_details"),
        FieldPanel("price"),
        FieldPanel("price_details"),
    ]


class ResourcePage(Page):
    """
    Basic resource page for all resource page.
    """

    template = "resource_template.html"
    parent_page_types = ["HomePage"]

    header_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload a header image that will render in the resource page.",
    )

    content = StreamField(
        [("content", ResourceBlock())],
        blank=False,
        help_text="Enter details of content.",
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel("header_image"),
        StreamFieldPanel("content"),
    ]

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "site_name": settings.SITE_NAME,
            "CSOURCE_PAYLOAD": None,
        }


@register_snippet
class SiteNotification(models.Model):
    """ Snippet model for showing site notifications. """

    message = RichTextField(
        max_length=255, features=["bold", "italic", "link", "document-link"]
    )

    panels = [FieldPanel("message")]

    def __str__(self):
        return str(self.message)


class HomeAlumniSection(BootcampRunChildPage):
    """
    Page that holds general alumni information on HomePage.
    """

    banner_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that will display as a banner at the top of the section, must be at least 750x505 pixels.",
    )
    heading = models.CharField(
        max_length=100, help_text="The heading to display on this section."
    )
    text = RichTextField(
        blank=False,
        help_text="Extra text to appear besides alumni quotes in this section.",
    )
    highlight_quote = models.CharField(
        null=True,
        max_length=255,
        help_text="Highlighted quote to display for this section.",
    )
    highlight_name = models.CharField(
        max_length=100, help_text="Name of the alumni for the highlighted quote."
    )

    content_panels = [
        ImageChooserPanel("banner_image"),
        FieldPanel("heading"),
        FieldPanel("text"),
        FieldPanel("highlight_quote"),
        FieldPanel("highlight_name"),
    ]

    class Meta:
        verbose_name = "Homepage Alumni Section"


class AlumniSection(BootcampRunChildPage):
    """
    Page that holds alumni for a product
    """

    banner_image = models.ForeignKey(
        Image,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that will display as a banner at the top of the section, must be at least 750x505 pixels.",
    )
    heading = models.CharField(
        max_length=100,
        default="Alumni",
        help_text="The heading to display on this section.",
    )
    text = RichTextField(
        blank=False,
        help_text="Extra text to appear besides alumni quotes in this section.",
    )
    highlight_quote = models.CharField(
        null=True,
        max_length=255,
        help_text="Highlighted quote to display for this section.",
    )
    highlight_name = models.CharField(
        max_length=100, help_text="Name of the alumni for the highlighted quote."
    )
    alumni_bios = StreamField(
        [("alumni", AlumniBlock())],
        blank=False,
        help_text="Alumni to display in this section.",
    )
    content_panels = [
        ImageChooserPanel("banner_image"),
        FieldPanel("heading"),
        FieldPanel("text"),
        FieldPanel("highlight_quote"),
        FieldPanel("highlight_name"),
        StreamFieldPanel("alumni_bios"),
    ]

    class Meta:
        verbose_name = "Alumni Section"


class LearningResourceSection(BootcampRunChildPage):
    """
    Page that holds the learning resources for a product
    """

    heading = models.CharField(
        max_length=100,
        default="Learning Resources",
        help_text="The heading to display on this section.",
    )
    items = StreamField(
        [("item", TitleLinksBlock())],
        help_text="The resources with links to display in this section",
    )

    content_panels = [FieldPanel("heading"), StreamFieldPanel("items")]

    class Meta:
        verbose_name = "Learning Resources Section"


class CatalogGridSection(BootcampRunChildPage):
    """
    Page that represents the catalog section on the home page
    """

    parent_page_types = ["HomePage"]

    contents = StreamField(
        [("bootcamp_run", CatalogSectionBootcampBlock())],
        help_text="The bootcamps to display in this catalog section",
        blank=True,
    )
    content_panels = [StreamFieldPanel("contents")]


class LetterTemplatePage(Page):
    """Page that represents an acceptance or rejection letter to be displayed and sent to a user"""

    max_count = 1  # make this a singleton
    acceptance_text = RichTextField(
        default=ACCEPTANCE_DEFAULT_LETTER_TEXT.replace("\n", "<br />\n")
    )
    rejection_text = RichTextField(
        default=REJECTION_DEFAULT_LETTER_TEXT.replace("\n", "<br />\n")
    )
    signatory_name = models.CharField(
        max_length=100, default="", help_text="Name of the signatory."
    )
    signature_image = models.ForeignKey(
        Image,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Upload an image that will render in the program description section.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("acceptance_text"),
        FieldPanel("rejection_text"),
        FieldPanel("signatory_name"),
        ImageChooserPanel("signature_image"),
    ]

    base_form_class = LetterTemplatePageForm

    # pylint: disable=unused-argument
    def serve_preview(self, request, *args, **kwargs):
        """
        Show a sample letter for testing
        """
        content = f"""
<h2>Acceptance letter:</h2><br />
{render_template(text=self.acceptance_text, context=SAMPLE_DECISION_TEMPLATE_CONTEXT)}<br />
<br />
<h2>Rejection letter:</h2><br />
{render_template(text=self.rejection_text, context=SAMPLE_DECISION_TEMPLATE_CONTEXT)}
"""
        signatory = {"name": self.signatory_name, "image": self.signature_image}
        return render(
            request,
            "letter_template_page.html",
            context={"preview": True, "content": content, "signatory": signatory},
        )

    def serve(self, request, *args, **kwargs):
        """Applicants should use LettersView to see their letters"""
        raise Http404


@register_setting
class ResourcePagesSettings(BaseSetting):
    """Wagtail settings for site pages"""

    apply_page = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    about_us_page = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    bootcamps_programs_page = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    terms_of_service_page = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )
    privacy_policy_page = models.ForeignKey(
        Page, null=True, on_delete=models.SET_NULL, related_name="+"
    )

    panels = [
        PageChooserPanel("apply_page"),
        PageChooserPanel("about_us_page"),
        PageChooserPanel("bootcamps_programs_page"),
        PageChooserPanel("terms_of_service_page"),
        PageChooserPanel("privacy_policy_page"),
    ]

    class Meta:
        verbose_name = "Resource Pages"


class SignatoryObjectIndexPage(Page):
    """
    A placeholder class to group signatory object pages as children.
    This class logically acts as no more than a "folder" to organize
    pages and add parent slug segment to the page url.
    """

    class Meta:
        abstract = True

    parent_page_types = ["HomePage"]
    subpage_types = ["SignatoryPage"]

    @classmethod
    def can_create_at(cls, parent):
        """
        You can only create one of these pages under the home page.
        The parent is limited via the `parent_page_type` list.
        """
        return (
            super().can_create_at(parent)
            and not parent.get_children().type(cls).exists()
        )

    def serve(self, request, *args, **kwargs):
        """
        For index pages we raise a 404 because these pages do not have a template
        of their own and we do not expect a page to available at their slug.
        """
        raise Http404


class SignatoryIndexPage(SignatoryObjectIndexPage):
    """
    A placeholder page to group all the signatories under it as well
    as consequently add /signatories/ to the signatory page urls
    """

    slug = SIGNATORY_INDEX_SLUG


class SignatoryPage(Page):
    """ CMS page representing a Signatory. """

    promote_panels = []
    parent_page_types = [SignatoryIndexPage]
    subpage_types = []

    name = models.CharField(
        max_length=250, null=False, blank=False, help_text="Name of the signatory."
    )
    title_1 = models.CharField(
        max_length=250,
        blank=True,
        help_text="Specify signatory first title in organization.",
    )
    title_2 = models.CharField(
        max_length=250,
        blank=True,
        help_text="Specify signatory second title in organization.",
    )
    organization = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Specify the organization of signatory.",
    )

    signature_image = models.ForeignKey(
        Image,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Signature image size must be at least 150x50 pixels.",
    )

    class Meta:
        verbose_name = "Signatory"

    content_panels = [
        FieldPanel("name"),
        FieldPanel("title_1"),
        FieldPanel("title_2"),
        FieldPanel("organization"),
        ImageChooserPanel("signature_image"),
    ]

    def save(self, *args, **kwargs):  # pylint: disable=signature-differs
        # auto generate a unique slug so we don't hit a ValidationError
        if not self.title:
            self.title = self.__class__._meta.verbose_name.title() + "-" + self.name

        self.slug = slugify("{}-{}".format(self.title, self.id))
        super().save(*args, **kwargs)

    def serve(self, request, *args, **kwargs):
        """
        As the name suggests these pages are going to be children of some other page. They are not
        designed to be viewed on their own so we raise a 404 if someone tries to access their slug.
        """
        raise Http404


class CertificateIndexPage(RoutablePageMixin, Page):
    """
    Certificate index page placeholder that handles routes for serving
    certificates given by UUID
    """

    parent_page_types = ["HomePage"]
    subpage_types = []

    slug = CERTIFICATE_INDEX_SLUG

    @classmethod
    def can_create_at(cls, parent):
        """
        You can only create one of these pages under the home page.
        The parent is limited via the `parent_page_type` list.
        """
        return (
            super().can_create_at(parent)
            and not parent.get_children().type(cls).exists()
        )

    @route(r"^([A-Fa-f0-9-]+)/?$")
    def bootcamp_certificate(
        self, request, uuid, *args, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Serve a bootcamp certificate by uuid
        """
        # Return 404 if certificates feature is disabled
        if not settings.FEATURES.get("ENABLE_CERTIFICATE_USER_VIEW", False):
            raise Http404()

        # Try to fetch a certificate by the uuid passed in the URL
        try:
            certificate = BootcampRunCertificate.objects.get(
                uuid=uuid, is_revoked=False
            )
        except BootcampRunCertificate.DoesNotExist:
            raise Http404()
        # Get a CertificatePage to serve this request
        certificate_page = (
            certificate.bootcamp_run.page.certificate_page
            if certificate.bootcamp_run.page
            else None
        )
        if not certificate_page:
            raise Http404()

        certificate_page.certificate = certificate
        return certificate_page.serve(request)

    @route(r"^$")
    def index_route(self, request, *args, **kwargs):
        """
        The index page is not meant to be served/viewed directly
        """
        raise Http404()


class CertificatePage(BootcampRunChildPage):
    """
    CMS page representing a Certificate.
    """

    template = "certificate_page.html"
    parent_page_types = ["BootcampRunPage"]

    bootcamp_run_name = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        help_text="Specify the bootcamp run name. e.g. 'MIT Innovation and Entrepreneurship Bootcamp' ",
    )

    granting_institution = models.CharField(
        max_length=250,
        null=False,
        blank=False,
        default="Massachusetts Institute of Technology",
        help_text="Specify the granting institution name. e.g. MIT Bootcamps & Harvard Medical School Center for Primary Care.",
    )

    certificate_name = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Specify the bootcamp certificate name. e.g. 'Certificate in New Ventures Leadership'",
    )

    location = models.CharField(
        max_length=250,
        blank=True,
        help_text="Optional text field for bootcamp location. e.g. 'Brisbane, Australia'",
    )

    secondary_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Representing the institution image, This image will be rendered over the certificate as secondary image.",
    )

    signatories = StreamField(
        StreamBlock(
            [
                (
                    "signatory",
                    PageChooserBlock(required=True, target_model=["cms.SignatoryPage"]),
                )
            ],
            min_num=1,
            max_num=5,
        ),
        help_text="You can choose upto 5 signatories.",
    )

    content_panels = [
        FieldPanel("bootcamp_run_name"),
        FieldPanel("granting_institution"),
        FieldPanel("certificate_name"),
        FieldPanel("location"),
        ImageChooserPanel("secondary_image"),
        StreamFieldPanel("signatories"),
    ]

    class Meta:
        verbose_name = "Certificate"

    def __init__(self, *args, **kwargs):
        self.certificate = None
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # auto generate a unique slug so we don't hit a ValidationError
        self.title = (
            self.__class__._meta.verbose_name.title()
            + " For "
            + self.get_parent().title
        )

        self.slug = slugify("certificate-{}".format(self.get_parent().id))
        Page.save(self, *args, **kwargs)

    def serve(self, request, *args, **kwargs):
        """
        We need to serve the certificate template for preview.
        """
        return Page.serve(self, request, *args, **kwargs)

    @property
    def signatory_pages(self):
        """
        Extracts all the pages out of the `signatories` stream into a list
        """
        pages = []
        for block in self.signatories:  # pylint: disable=not-an-iterable
            if block.value:
                pages.append(block.value.specific)
        return pages

    def get_context(self, request, *args, **kwargs):
        preview_context = {}
        context = {}
        parent = self.parent()
        if request.is_preview:
            preview_context = {
                "learner_name": "Anthony M. Stark",
                "start_date": parent.bootcamp_run.start_date
                if parent.bootcamp_run
                else datetime.now(),
                "end_date": parent.bootcamp_run.end_date
                if parent.bootcamp_run
                else datetime.now(),
                "location": self.location if self.location else "Brisbane, Australia",
                "certificate_user": None,
            }
        elif self.certificate:
            # Verify that the certificate in fact is for this same course
            if parent.bootcamp_run.id != self.certificate.bootcamp_run.id:
                raise Http404()
            start_date, end_date = self.certificate.start_end_dates
            context = {
                "uuid": self.certificate.uuid,
                "certificate_user": self.certificate.user,
                "learner_name": self.certificate.user.profile.name,
                "start_date": start_date,
                "end_date": end_date,
                "location": self.location,
            }
        else:
            raise Http404()

        # The share image url needs to be absolute
        return {
            "site_name": settings.SITE_NAME,
            "share_image_url": urljoin(
                request.build_absolute_uri("///"),
                static("images/certificates/share-image.png"),
            ),
            "share_text": "I just earned a certificate in {}".format(
                self.bootcamp_run_name
            ),
            **super().get_context(request, *args, **kwargs),
            **preview_context,
            **context,
        }
