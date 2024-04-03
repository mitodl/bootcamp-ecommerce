"""CMS signals"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from wagtail.signals import page_published

from cms.models import ResourcePagesSettings
from cms.utils import invalidate_resource_page_urls


@receiver(page_published)
def resource_page_published(sender, **kwargs):  # pylint: disable=unused-argument
    """Invalidate the cached values whenever a page is published"""
    invalidate_resource_page_urls()


@receiver(post_save, sender=ResourcePagesSettings)
def resource_page_settings_change(sender, **kwargs):  # pylint: disable=unused-argument
    """Invalidate the cached values whenver the settings are saved"""
    invalidate_resource_page_urls()
