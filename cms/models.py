"""
Page models for the CMS
"""
from django.db import models
from django.utils.text import slugify
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.images.models import Image
from wagtail.core import blocks
from wagtail.core.models import Page
from cms.blocks import ResourceBlock


class BootcampPage(Page):
    """
    CMS page representing a Bootcamp Page
    """

    class Meta:
        abstract = True

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

class BootcampRunPage(BootcampPage):
    """
    CMS page representing a klass
    """

    template = "product_page.html"

    klasses = models.OneToOneField(
        "klasses.Klass",
        null=True,
        on_delete=models.SET_NULL,
        help_text="The Klass for this page",
    )

    content_panels = BootcampPage.content_panels + [FieldPanel("klasses")]

    @property
    def product(self):
        """Gets the product associated with this page"""
        return self.klasses

    def get_context(self, request, *args, **kwargs):
        """
        return page context.
        """
        context = super(BootcampRunPage, self).get_context(request)
        return context

    def save(self, *args, **kwargs):
        # autogenerate a unique slug so we don't hit a ValidationError
        if not self.title:
            self.title = self.__class__._meta.verbose_name.title()
        self.slug = slugify("bootcamp-{}".format(self.product.klass_key))
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
        context = super(ResourcePage, self).get_context(request)

        return context
