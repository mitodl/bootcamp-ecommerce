"""
Page models for the CMS
"""
import json

from django.db import models
from django.utils.text import slugify
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.models import Image

from cms.blocks import ResourceBlock
from main.views import _serialize_js_settings


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

    def get_context(self, request, *args, **kwargs):
        return {
            **super().get_context(request),
            "js_settings_json": json.dumps(_serialize_js_settings(request)),
            "title": self.title,
        }



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

    content_panels = BootcampPage.content_panels + [FieldPanel("bootcamp_run")]

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
        context = super().get_context(request)

        return context
