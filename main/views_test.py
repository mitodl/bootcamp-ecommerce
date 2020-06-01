"""
Test end to end django views.
"""
import pytest
from cms import factories


@pytest.mark.django_db
def test_index_anonymous(settings, mocker, client):
    """Verify the index view is as expected when user is anonymous"""
    settings.USE_WEBPACK_DEV_SERVER = False
    settings.ZENDESK_CONFIG = {
        "HELP_WIDGET_ENABLED": False,
        "HELP_WIDGET_KEY": "fake_key",
    }

    patched_get_bundle = mocker.patch("main.templatetags.render_bundle._get_bundle")
    root_page = factories.HomePageFactory(parent=None)
    resp = client.get("/")
    assert resp.status_code == 200
    assert root_page.title in resp.content.decode("utf-8")
    assert resp.context["page"] == root_page

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
def test_password_reset_link(client):
    """Verify that the password reset link doesn't cause an error"""
    resp = client.get("/signin/forgot-password/confirm/MTA3/5gw-ccd72e49361be41f4924/")
    assert resp.status_code == 200
