"""Tests for URLs"""
from django.urls import reverse, resolve

from main.features import CMS_HOME_PAGE
from main.test_utils import reload_urlconf, patched_feature_enabled
from main.views import index as deprecated_index


def test_urls():
    """Make sure URLs match with resolved names"""
    assert reverse("create-payment") == "/api/v0/payment/"
    assert reverse("order-fulfillment") == "/api/v0/order_fulfillment/"


def test_cms_home_page_feature_flag(mocker):
    """Tests that the CMS home page feature flag correctly sets the view to handle the root URL"""
    feature_enabled_patch = mocker.patch(
        "main.features.is_enabled",
        side_effect=patched_feature_enabled({CMS_HOME_PAGE: False}),
    )
    reload_urlconf()
    view = resolve("/")
    assert view.func == deprecated_index  # pylint: disable=comparison-with-callable
    feature_enabled_patch.assert_called_once_with(CMS_HOME_PAGE)
    feature_enabled_patch.reset_mock()
    feature_enabled_patch = mocker.patch(
        "main.features.is_enabled",
        side_effect=patched_feature_enabled({CMS_HOME_PAGE: True}),
    )
    reload_urlconf()
    view = resolve("/")
    assert view.view_name == "wagtail_serve"
    feature_enabled_patch.assert_called_once_with(CMS_HOME_PAGE)
