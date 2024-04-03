"""CMS signals tests"""

import pytest

from cms.factories import (
    ResourcePageFactory,
    HomePageFactory,
    BootcampIndexPageFactory,
    BootcampRunPageFactory,
    ResourcePagesSettingsFactory,
)

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "page_factory",
    [
        HomePageFactory,
        BootcampIndexPageFactory,
        BootcampRunPageFactory,
        ResourcePageFactory,
    ],
)
def test_resource_page_published(mocker, page_factory):
    """Test that resource_page_published fires and calls invalidate_resource_page_urls"""
    mock_invalidate_resource_page_urls = mocker.patch(
        "cms.signals.invalidate_resource_page_urls"
    )

    page = page_factory.create()
    revision = page.save_revision()
    revision.publish()
    assert mock_invalidate_resource_page_urls.call_count == 1


def test_resource_page_settings_change(mocker):
    """Verify that resource_page_settings_change fires and calls invalidate_resource_page_urls"""
    mock_invalidate_resource_page_urls = mocker.patch(
        "cms.signals.invalidate_resource_page_urls"
    )

    page_settings = ResourcePagesSettingsFactory.create()
    page_settings.save()
    # one for create, one for update
    assert mock_invalidate_resource_page_urls.call_count == 2
