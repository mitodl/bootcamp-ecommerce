"""Tests for CMS serializers"""
import pytest

from cms.factories import BootcampRunPageFactory
from cms.serializers import BootcampRunPageSerializer


@pytest.mark.django_db
def test_bootcamp_run_page_serializer(mocker):
    """The bootcamp run page serializer should include the expected fields"""
    bootcamp_run_page = BootcampRunPageFactory.build()
    fake_image_url = "fake-image.jpg"
    mocker.patch("cms.serializers.image_version_url", return_value=fake_image_url)
    serialized = BootcampRunPageSerializer(instance=bootcamp_run_page).data
    assert serialized == {
        "description": bootcamp_run_page.description,
        "subhead": bootcamp_run_page.subhead,
        "thumbnail_image_src": fake_image_url,
    }
    bootcamp_run_page.thumbnail_image = None
    serialized = BootcampRunPageSerializer(instance=bootcamp_run_page).data
    assert serialized["thumbnail_image_src"] is None
