"""
Page models for the CMS
"""
import json

from django.conf import settings
from django.db import models
from django.http.response import Http404
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.utils import WAGTAIL_APPEND_SLASH
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image
from wagtail.core.blocks import StreamBlock
from wagtail.snippets.models import register_snippet

from cms.blocks import (
    ResourceBlock,
    InstructorSectionBlock,
    ThreeColumnImageTextBlock,
    AlumniBlock,
    TitleLinksBlock,
    TitleDescriptionBlock,
)

from main.views import _serialize_js_settings


class HomePage(Page):
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
            "js_settings_json": json.dumps(_serialize_js_settings(request)),
            "site_name": settings.SITE_NAME,
            "title": self.title,
        }


class BootcampPage(Page):
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

    def _get_child_page_of_type(self, cls):
        """Gets the first child page of the given type if it exists"""
        child = self.get_children().type(cls).live().first()
        return child.specific if child else None

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "js_settings_json": json.dumps(_serialize_js_settings(request)),
            "site_name": settings.SITE_NAME,
            "title": self.title,
            "site_name": settings.SITE_NAME,
            # The context variables below are added to avoid duplicate queries within the templates
            "three_column_image_text_section": self.three_column_image_text_section,
            "program_description_section": self.program_description_section,
        }

    @property
    def instructors(self):
        """Gets the faculty members page"""
        return self._get_child_page_of_type(InstructorsPage)

    @property
    def three_column_image_text_section(self):
        """Gets the three column image text section child page"""
        return self._get_child_page_of_type(ThreeColumnImageTextPage)

    @property
    def program_description_section(self):
        """Gets the program description page"""
        return self._get_child_page_of_type(ProgramDescriptionPage)

    @property
    def alumni(self):
        """Gets the faculty members page"""
        return self._get_child_page_of_type(AlumniPage)

    @property
    def learning_resources(self):
        """Get the learning resources page"""
        return self._get_child_page_of_type(LearningResourcePage)

    subpage_types = [
        "ThreeColumnImageTextPage",
        "ProgramDescriptionPage",
        "InstructorsPage",
        "AlumniPage",
        "LearningResourcePage",
    ]


class BootcampRunPage(BootcampPage):
    """
    CMS page representing a bootcamp run
    """

    template = "product_page.html"

    bootcamp_run = models.OneToOneField(
        "klasses.BootcampRun",
        null=True,
        on_delete=models.SET_NULL,
        help_text="The bootcamp run for this page",
    )

    content_panels = [FieldPanel("bootcamp_run")] + BootcampPage.content_panels

    def get_context(self, request, *args, **kwargs):
        """
        return page context.
        """
        context = super().get_context(request)
        return context

    def save(self, *args, **kwargs):
        # autogenerate a unique slug so we don't hit a ValidationError
        if not self.title:
            self.title = self.__class__._meta.verbose_name.title()
        self.slug = slugify("bootcamp-{}".format(self.bootcamp_run.run_key))
        super().save(*args, **kwargs)


class BootcampRunChildPage(Page):
    """
    Abstract page representing a child of BootcampRun Page
    """

    class Meta:
        abstract = True

    parent_page_types = ["BootcampRunPage"]

    # disable promote panels, no need for slug entry, it will be autogenerated
    promote_panels = []

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


class ThreeColumnImageTextPage(BootcampRunChildPage):
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


class ProgramDescriptionPage(BootcampRunChildPage):
    """
    Describe the bootcamp program.
    """

    statement = RichTextField(
        blank=True, help_text="The bold statement for the bootcamp program."
    )
    heading = models.CharField(
        max_length=255,
        default="Program Description",
        help_text="The heading to display in the header section on the page.",
    )
    body = RichTextField(
        help_text="The body text to display in the header section on the page."
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
        StreamFieldPanel("steps"),
    ]


class InstructorsPage(BootcampRunChildPage):
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


class ResourcePage(Page):
    """
    Basic resource page for all resource page.
    """

    template = "resource_template.html"

    sub_heading = models.CharField(
        max_length=250,
        null=True,
        blank=True,
        help_text="Sub heading of the resource page.",
    )

    content = StreamField(
        [("content", ResourceBlock())],
        blank=False,
        help_text="Enter details of content.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("content"),
    ]

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request, *args, **kwargs),
            "site_name": settings.SITE_NAME,
        }


@register_snippet
class SiteNotification(models.Model):
    """ Snippet model for showing site notifications. """

    message = RichTextField(
        max_length=255, features=["bold", "italic", "link", "document-link"]
    )

    panels = [FieldPanel("message")]

    def __str__(self):
        return self.message


class AlumniPage(BootcampRunChildPage):
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


class LearningResourcePage(BootcampRunChildPage):
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
