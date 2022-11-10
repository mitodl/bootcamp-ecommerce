"""Tests for CMS serializers"""
import pytest

from cms.factories import AdmissionSectionFactory, BootcampRunPageFactory
from cms.serializers import BootcampRunPageSerializer


@pytest.mark.django_db
def test_bootcamp_run_page_serializer(mocker):
    """The bootcamp run page serializer should include the expected fields"""
    bootcamp_run_page = BootcampRunPageFactory.create()
    AdmissionSectionFactory.create(
        parent=bootcamp_run_page,
        admissions_image__title="title of the image",
        notes="notes",
        details="details",
        bootcamp_location="bootcamp location",
        bootcamp_location_details="location details",
        dates="dates",
        dates_details="dates details",
        price=10,
        price_details="price details",
    )
    fake_image_url = "fake-image.jpg"
    mocker.patch("cms.serializers.image_version_url", return_value=fake_image_url)
    serialized = BootcampRunPageSerializer(instance=bootcamp_run_page).data
    assert serialized == {
        "description": bootcamp_run_page.description,
        "subhead": bootcamp_run_page.subhead,
        "thumbnail_image_src": fake_image_url,
        "bootcamp_location": "bootcamp location",
        "bootcamp_location_details": "location details",
    }
    bootcamp_run_page.thumbnail_image = None
    serialized = BootcampRunPageSerializer(instance=bootcamp_run_page).data
    assert serialized["thumbnail_image_src"] is None


@pytest.mark.django_db
def test_bootcamp_run_page_serializer_without_admission_page(mocker):
    """The bootcamp run page serializer should define None for location fields if no admission page exists"""
    bootcamp_run_page = BootcampRunPageFactory.create()
    fake_image_url = "fake-image.jpg"
    mocker.patch("cms.serializers.image_version_url", return_value=fake_image_url)
    serialized = BootcampRunPageSerializer(instance=bootcamp_run_page).data
    assert serialized == {
        "description": bootcamp_run_page.description,
        "subhead": bootcamp_run_page.subhead,
        "thumbnail_image_src": fake_image_url,
        "bootcamp_location": None,
        "bootcamp_location_details": None,
    }
