"""Utils tests"""
import pytest

from cms.factories import ResourcePagesSettingsFactory, ResourcePageFactory
from cms.utils import get_resource_page_urls, invalidate_get_resource_page_urls

pytestmark = pytest.mark.django_db


def test_get_resource_page_urls():
    """Tests get_resource_page_urls() returns a dictionary of page urls"""
    site_page_settings = ResourcePagesSettingsFactory.create()

    assert get_resource_page_urls(site_page_settings.site) == {
        "about_us": site_page_settings.about_us_page.url,
        "how_to_apply": site_page_settings.apply_page.url,
        "bootcamps_programs": site_page_settings.bootcamps_programs_page.url,
        "privacy_policy": site_page_settings.privacy_policy_page.url,
        "terms_of_service": site_page_settings.terms_of_service_page.url,
    }


def test_invalidate_get_resource_page_urls():
    """Test that invalidate_get_resource_page_urls() invalidates the cache for get_resource_page_urls"""
    site_page_settings = ResourcePagesSettingsFactory.create()
    initial = get_resource_page_urls(site_page_settings.site)

    site_page_settings.privacy_policy_page = ResourcePageFactory.create()
    site_page_settings.save()

    # after we invalidate the cache, we should see this updated url
    expected = {**initial, "privacy_policy": site_page_settings.privacy_policy_page.url}
    # verify the calue is cached
    assert get_resource_page_urls(site_page_settings.site) == initial

    invalidate_get_resource_page_urls()

    # updated value should be seen
    assert get_resource_page_urls(site_page_settings.site) == expected
