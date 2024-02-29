"""Tests for custom CMS templatetags"""

from datetime import date

import pytest
from wagtail.images.views.serve import generate_signature
from wagtail_factories import ImageFactory

from cms.templatetags.bootcamp_duration_format import bootcamp_duration_format
from cms.templatetags.image_version_url import image_version_url


@pytest.mark.django_db
def test_image_version_url():
    """image_version_url should produce an image URL with the file hash set as the file version in the querystring"""
    view_name = "wagtailimages_serve"
    image_id = 1
    file_hash = "abcdefg"
    image_filter = "fill-75x75"
    image = ImageFactory.build(id=image_id, file_hash=file_hash)
    expected_signature = generate_signature(image_id, image_filter, key=None)
    result_url = image_version_url(image, image_filter, viewname=view_name)
    assert (
        result_url
        == f"/images/{expected_signature}/{image_id}/{image_filter}/?v={file_hash}"
    )


@pytest.mark.parametrize(
    "start, end, expected_format",
    [
        [date(2024, 1, 15), date(2024, 1, 17), "January 15 - 17, 2024"],
        [date(2024, 1, 15), date(2024, 2, 15), "January 15 - February 15, 2024"],
        [date(2024, 1, 15), date(2025, 1, 15), "January 15, 2024 - January 15, 2025"],
        [date(2024, 1, 15), date(2025, 2, 15), "January 15, 2024 - February 15, 2025"],
    ],
)
def test_bootcamp_duration_format(start, end, expected_format):
    """bootcamp_duration_format should format the duration correctly"""
    assert bootcamp_duration_format(start, end) == expected_format
