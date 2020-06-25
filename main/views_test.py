"""
Test end to end django views.
"""
import json
import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory

from cms import factories
from main import features
from main.views import get_base_context
from profiles.factories import UserFactory


@pytest.mark.django_db
@pytest.mark.parametrize("is_authed", [True, False])
@pytest.mark.parametrize("feat_social_auth", [True, False])
def test_get_base_context(settings, mocker, is_authed, feat_social_auth):
    """Verify the context that is provided to all Django templates inheriting from the base template"""
    settings.FEATURES[features.SOCIAL_AUTH_API] = feat_social_auth
    fake_js_settings = {"js": "settings"}
    patched_json_settings = mocker.patch(
        "main.views._serialize_js_settings", return_value=fake_js_settings
    )
    user = UserFactory.create() if is_authed else AnonymousUser()

    request = RequestFactory().get("/")
    request.user = user
    context = get_base_context(request)
    assert context == {
        "js_settings_json": json.dumps(fake_js_settings),
        "resource_page_urls": {
            "how_to_apply": "/apply",
            "about_us": "/about-us",
            "bootcamps_programs": "/bootcamps-programs",
            "privacy_policy": "/privacy-policy",
        },
        "authenticated": is_authed,
        "social_auth_enabled": feat_social_auth,
    }
    patched_json_settings.assert_called_once_with(request)


def test_get_context_js_settings(settings):
    """Verify the specific JS settings in the base context dictionary"""
    settings.USE_WEBPACK_DEV_SERVER = False
    settings.ENVIRONMENT = "TEST"
    settings.VERSION = "9.9.9"
    settings.RECAPTCHA_SITE_KEY = "SITE_KEY"
    settings.SUPPORT_URL = "http://example.com/support"
    settings.SENTRY_DSN = "http://example.com/sentry"
    settings.ZENDESK_CONFIG = {
        "HELP_WIDGET_ENABLED": False,
        "HELP_WIDGET_KEY": "fake_key",
    }

    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    context = get_base_context(request)
    js_settings = json.loads(context["js_settings_json"])
    assert js_settings == {
        "environment": settings.ENVIRONMENT,
        "release_version": settings.VERSION,
        "sentry_dsn": settings.SENTRY_DSN,
        "public_path": "/static/bundles/",
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG["HELP_WIDGET_ENABLED"],
            "help_widget_key": settings.ZENDESK_CONFIG["HELP_WIDGET_KEY"],
        },
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "support_url": settings.SUPPORT_URL,
    }


@pytest.mark.django_db
def test_index_anonymous(settings, mocker, client):
    """Verify the index view is as expected when user is anonymous"""
    settings.USE_WEBPACK_DEV_SERVER = False

    patched_get_bundle = mocker.patch("main.templatetags.render_bundle._get_bundle")
    root_page = factories.HomePageFactory(parent=None)
    resp = client.get("/")
    assert resp.status_code == 200
    assert root_page.title in resp.content.decode("utf-8")
    assert resp.context["page"] == root_page

    bundles = [bundle[0][1] for bundle in patched_get_bundle.call_args_list]
    assert set(bundles) == {"header", "sentry_client", "style", "third_party"}


@pytest.mark.django_db
def test_password_reset_link(client):
    """Verify that the password reset link doesn't cause an error"""
    resp = client.get("/signin/forgot-password/confirm/MTA3/5gw-ccd72e49361be41f4924/")
    assert resp.status_code == 200
