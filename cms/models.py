"""
Page models for the CMS
"""
import logging

from django.conf import settings
from django.db import models, transaction
from django.http.response import Http404
from django.urls import reverse
from django.utils.text import slugify
from django.shortcuts import render
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel, PageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.core.blocks import StreamBlock
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
    REJECTION_DEFAULT_LETTER_TEXT,
    SAMPLE_DECISION_TEMPLATE_CONTEXT,
)
from cms.forms import LetterTemplatePageForm


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
            "site_name": settings.SITE_NAME,
            "title": self.title,
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
        on_delete=models.SET_NULL,
        help_text="The bootcamp run for this page",
    )

    content_panels = [FieldPanel("bootcamp_run")] + BootcampPage.content_panels


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

    def save(self, *args, **kwargs):
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
        }

    def save(self, *args, **kwargs):
        """Save the model instance"""
        from cms.utils import invalidate_get_resource_page_urls

        super().save(*args, **kwargs)
        transaction.on_commit(invalidate_get_resource_page_urls)


@register_snippet
class SiteNotification(models.Model):
    """ Snippet model for showing site notifications. """

    message = RichTextField(
        max_length=255, features=["bold", "italic", "link", "document-link"]
    )

    panels = [FieldPanel("message")]

    def __str__(self):
        return self.message


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

    content_panels = Page.content_panels + [
        FieldPanel("acceptance_text"),
        FieldPanel("rejection_text"),
    ]

    base_form_class = LetterTemplatePageForm

    def serve_preview(
        self, request, *args, **kwargs
    ):  # pylint: disable=arguments-differ
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
        return render(
            request,
            "letter_template_page.html",
            context={"preview": True, "content": content},
        )

    def serve(self, request, *args, **kwargs):
        """Applicants should use LettersView to see their letters"""
        raise Http404


@register_setting
class ResourcePagesSettings(BaseSetting):
    """Wagtail settings for site pages"""

    apply_page = models.ForeignKey(
        "wagtailcore.Page", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    about_us_page = models.ForeignKey(
        "wagtailcore.Page", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    bootcamps_programs_page = models.ForeignKey(
        "wagtailcore.Page", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    terms_of_service_page = models.ForeignKey(
        "wagtailcore.Page", null=True, on_delete=models.SET_NULL, related_name="+"
    )
    privacy_policy_page = models.ForeignKey(
        "wagtailcore.Page", null=True, on_delete=models.SET_NULL, related_name="+"
    )

    panels = [
        PageChooserPanel("apply_page"),
        PageChooserPanel("about_us_page"),
        PageChooserPanel("bootcamps_programs_page"),
        PageChooserPanel("terms_of_service_page"),
        PageChooserPanel("privacy_policy_page"),
    ]

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """Save the model instance"""
        from cms.utils import invalidate_get_resource_page_urls

        super().save(*args, **kwargs)
        transaction.on_commit(invalidate_get_resource_page_urls)

    class Meta:
        verbose_name = "Resource Pages"
