"""
Test end to end django views.
"""
import json
import pytest

from django.urls import reverse
from rest_framework.status import HTTP_302_FOUND

from profiles.factories import UserFactory


@pytest.mark.django_db
def test_index_anonymous(settings, mocker, client):
    """Verify the index view is as expected when user is anonymous"""
    settings.USE_WEBPACK_DEV_SERVER = False
    settings.ZENDESK_CONFIG = {
        "HELP_WIDGET_ENABLED": False,
        "HELP_WIDGET_KEY": "fake_key",
    }

    patched_get_bundle = mocker.patch("main.templatetags.render_bundle._get_bundle")
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Pay Here for your MIT Bootcamp" in resp.content.decode("utf-8")

    bundles = [bundle[0][1] for bundle in patched_get_bundle.call_args_list]
    assert set(bundles) == {"sentry_client", "style", "third_party"}
    js_settings = json.loads(resp.context["js_settings_json"])
    assert js_settings == {
        "environment": settings.ENVIRONMENT,
        "release_version": settings.VERSION,
        "sentry_dsn": "",
        "public_path": "/static/bundles/",
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG["HELP_WIDGET_ENABLED"],
            "help_widget_key": settings.ZENDESK_CONFIG["HELP_WIDGET_KEY"],
        },
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "support_url": settings.SUPPORT_URL,
    }


@pytest.mark.django_db
def test_index_logged_in(client):
    """Verify the user is redirected to pay if logged in"""
    user = UserFactory.create()
    client.force_login(user)
    assert client.get(reverse("bootcamp-index")).status_code == HTTP_302_FOUND


@pytest.mark.django_db
def test_index_logged_in_post(client):
    """
    Verify the user is redirected to the applications dashboard if logged in on a POST request
    without CSRF token and that the GET parameters are kept
    """
    user = UserFactory.create()
    client.force_login(user)
    resp = client.post(reverse("bootcamp-index") + "?foo=bar")
    assert resp.status_code == HTTP_302_FOUND
    assert resp.url == reverse("applications") + "?foo=bar"
