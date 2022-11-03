"""Context processors tests"""
import json
import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from main.context_processors import configuration_context, js_settings
from profiles.factories import UserFactory


# pylint: disable=redefined-outer-name
@pytest.fixture
def patched_get_resource_page_urls(mocker):
    """Return a mock of main.context_processors.get_resource_page_urls"""
    yield mocker.patch(
        "main.context_processors.get_resource_page_urls",
        return_value={"terms_of_service": "/terms-of-service"},
    )


@pytest.mark.django_db
@pytest.mark.parametrize("is_authed", [True, False])
def test_configuration_context(
    settings, mocker, is_authed, patched_get_resource_page_urls
):
    """Verify the context that is provided to all Django templates"""
    settings.ZENDESK_CONFIG = {
        "HELP_WIDGET_ENABLED": False,
        "HELP_WIDGET_KEY": "fake_key",
    }
    settings.HUBSPOT_CONFIG = {
        "HUBSPOT_PORTAL_ID": "fake-portal-id",
        "HUBSPOT_FOOTER_FORM_GUID": "fake-form-guid",
    }
    user = UserFactory.create() if is_authed else AnonymousUser()

    request = RequestFactory().get("/")
    request.user = user
    request.site = mocker.Mock()
    context = configuration_context(request)
    assert context == {
        "resource_page_urls": {"terms_of_service": "/terms-of-service"},
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG["HELP_WIDGET_ENABLED"],
            "help_widget_key": settings.ZENDESK_CONFIG["HELP_WIDGET_KEY"],
        },
        "hubspot_portal_id": settings.HUBSPOT_CONFIG.get("HUBSPOT_PORTAL_ID"),
        "hubspot_footer_form_guid": settings.HUBSPOT_CONFIG.get(
            "HUBSPOT_FOOTER_FORM_GUID"
        ),
        "support_url": settings.SUPPORT_URL,
    }
    patched_get_resource_page_urls.assert_called_once_with(request.site)


def test_get_context_js_settings(mocker, settings, patched_get_resource_page_urls):
    """Verify the specific JS settings in the base context dictionary"""
    settings.WEBPACK_USE_DEV_SERVER = False
    settings.ENVIRONMENT = "TEST"
    settings.VERSION = "9.9.9"
    settings.RECAPTCHA_SITE_KEY = "SITE_KEY"
    settings.SUPPORT_URL = "http://example.com/support"
    settings.SENTRY_DSN = "http://example.com/sentry"
    settings.MAX_FILE_UPLOAD_MB = 123
    settings.ZENDESK_CONFIG = {
        "HELP_WIDGET_ENABLED": False,
        "HELP_WIDGET_KEY": "fake_key",
    }

    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.site = mocker.Mock()
    context = js_settings(request)
    assert json.loads(context["js_settings_json"]) == {
        "environment": settings.ENVIRONMENT,
        "release_version": settings.VERSION,
        "sentry_dsn": settings.SENTRY_DSN,
        "public_path": "/static/bundles/",
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG["HELP_WIDGET_ENABLED"],
            "help_widget_key": settings.ZENDESK_CONFIG["HELP_WIDGET_KEY"],
        },
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "upload_max_size": 123_000_000,
        "support_url": settings.SUPPORT_URL,
        "terms_url": patched_get_resource_page_urls.return_value["terms_of_service"],
        "novoed_base_url": settings.NOVOED_BASE_URL,
    }
