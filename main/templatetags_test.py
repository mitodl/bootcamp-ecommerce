"""
Tests for templatetags in the main Django app
"""
# NOTE: This file is located here and not in main/templatetags/ because Django attempts to load
# all files in the 'templatetags' directory as template tags, even '_test.py' files.
from datetime import datetime

import pytest
from pytz import utc

from main.templatetags.dollar_format import dollar_format
from main.templatetags.parse_date import parse_iso_datetime

FAKE_COMMON_BUNDLE = [
    {
        "name": "common-1f11431a92820b453513.js",
        "path": "/project/static/bundles/common-1f11431a92820b453513.js",
    }
]


def test_dollar_format():
    """Test that dollar_format takes a number representing a dollar value and formats it correctly"""
    assert dollar_format("123") == "$123.00"
    assert dollar_format("123.5") == "$123.50"
    assert dollar_format(123) == "$123.00"
    assert dollar_format(123.5) == "$123.50"
    assert dollar_format(-34.56) == "-$34.56"


@pytest.fixture(autouse=True)
def render_bundle_settings(settings):
    """Settings for render_bundle_test"""
    settings.DISABLE_WEBPACK_LOADER_STATS = False


def test_parse_iso_datetime():
    """Test that parse_iso_datetime correctly formats an ISO 8601 date string"""
    parsed_datetime = parse_iso_datetime("2017-01-01T01:01:01.000000Z")
    assert parsed_datetime == datetime(
        year=2017, month=1, day=1, hour=1, minute=1, second=1, tzinfo=utc
    )
    assert parse_iso_datetime("invalid") is None
