"""
Page models for the CMS
"""
from django.db import models
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.models import Image
from wagtail.core import blocks
from wagtail.core.models import Page
from cms.blocks import ResourceBlock


class BootcampPage(Page):
    """
    CMS page representing a Bootcamp
    """
    description = RichTextField(
        blank=True, help_text="The description shown on the product page"
    )
    content = StreamField([
        ('rich_text', blocks.RichTextBlock())
    ], blank=True, help_text='The content of the benefits page')

    thumbnail_image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Thumbnail size must be at least 690x530 pixels.",
    )
    content_panels = Page.content_panels + [
        FieldPanel("description", classname="full"),
        FieldPanel("thumbnail_image"),
        StreamFieldPanel("content"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super(BootcampPage, self).get_context(request)
        context["title"] = self.title
        return context


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
        context = super(ResourcePage, self).get_context(request)

        return context
