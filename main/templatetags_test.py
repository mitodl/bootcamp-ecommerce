"""
Tests for templatetags in the main Django app
"""
# NOTE: This file is located here and not in main/templatetags/ because Django attempts to load
# all files in the 'templatetags' directory as template tags, even '_test.py' files.
from datetime import datetime

from django.test.client import RequestFactory
import pytest
from pytz import utc

from main.utils import webpack_dev_server_url
from main.templatetags.render_bundle import render_bundle, public_path
from main.templatetags.dollar_format import dollar_format
from main.templatetags.parse_date import parse_iso_datetime

FAKE_COMMON_BUNDLE = [
    {
        "name": "common-1f11431a92820b453513.js",
        "path": "/project/static/bundles/common-1f11431a92820b453513.js",
    }
]


@pytest.fixture(autouse=True)
def render_bundle_settings(settings):
    """Settings for render_bundle_test"""
    settings.DISABLE_WEBPACK_LOADER_STATS = False


def test_debug(settings, mocker):
    """
    If USE_WEBPACK_DEV_SERVER=True, return a hot reload URL
    """
    settings.USE_WEBPACK_DEV_SERVER = True
    request = RequestFactory().get("/")
    context = {"request": request}

    # convert to generator
    common_bundle = (chunk for chunk in FAKE_COMMON_BUNDLE)
    get_bundle = mocker.Mock(return_value=common_bundle)
    loader = mocker.Mock(get_bundle=get_bundle)
    bundle_name = "bundle_name"
    get_loader = mocker.patch(
        "main.templatetags.render_bundle.get_loader", return_value=loader
    )
    assert render_bundle(context, bundle_name) == (
        '<script type="text/javascript" src="{base}/{filename}" >'
        "</script>".format(
            base=webpack_dev_server_url(request), filename=FAKE_COMMON_BUNDLE[0]["name"]
        )
    )

    assert public_path(request) == webpack_dev_server_url(request) + "/"

    get_bundle.assert_called_with(bundle_name)
    get_loader.assert_called_with("DEFAULT")


def test_production(settings, mocker):
    """
    If USE_WEBPACK_DEV_SERVER=False, return a static URL for production
    """
    settings.USE_WEBPACK_DEV_SERVER = False
    request = RequestFactory().get("/")
    context = {"request": request}

    # convert to generator
    common_bundle = (chunk for chunk in FAKE_COMMON_BUNDLE)
    get_bundle = mocker.Mock(return_value=common_bundle)
    loader = mocker.Mock(get_bundle=get_bundle)
    bundle_name = "bundle_name"
    get_loader = mocker.patch(
        "main.templatetags.render_bundle.get_loader", return_value=loader
    )
    assert render_bundle(context, bundle_name) == (
        '<script type="text/javascript" src="{base}/{filename}" >'
        "</script>".format(
            base="/static/bundles", filename=FAKE_COMMON_BUNDLE[0]["name"]
        )
    )

    assert public_path(request) == "/static/bundles/"

    get_bundle.assert_called_with(bundle_name)
    get_loader.assert_called_with("DEFAULT")


def test_missing_file(mocker):
    """
    If webpack-stats.json is missing, return an empty string
    """
    request = RequestFactory().get("/")
    context = {"request": request}

    get_bundle = mocker.Mock(side_effect=OSError)
    loader = mocker.Mock(get_bundle=get_bundle)
    bundle_name = "bundle_name"
    get_loader = mocker.patch(
        "main.templatetags.render_bundle.get_loader", return_value=loader
    )
    assert render_bundle(context, bundle_name) == ""

    get_bundle.assert_called_with(bundle_name)
    get_loader.assert_called_with("DEFAULT")


def test_dollar_format():
    """Test that dollar_format takes a number representing a dollar value and formats it correctly"""
    assert dollar_format("123") == "$123.00"
    assert dollar_format("123.5") == "$123.50"
    assert dollar_format(123) == "$123.00"
    assert dollar_format(123.5) == "$123.50"


def test_parse_iso_datetime():
    """Test that parse_iso_datetime correctly formats an ISO 8601 date string"""
    parsed_datetime = parse_iso_datetime("2017-01-01T01:01:01.000000Z")
    assert parsed_datetime == datetime(
        year=2017, month=1, day=1, hour=1, minute=1, second=1, tzinfo=utc
    )
    assert parse_iso_datetime("invalid") is None
