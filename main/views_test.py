"""
Test end to end django views.
"""

import json

import pytest
from django.urls import reverse

from cms.factories import HomePageFactory


@pytest.mark.django_db
def test_index_anonymous(settings, mocker, client):
    """Verify the index view is as expected when user is anonymous"""
    settings.WEBPACK_USE_DEV_SERVER = False

    patched_get_bundle = mocker.patch(
        "mitol.common.templatetags.render_bundle._get_bundle"
    )
    root_page = HomePageFactory.create(parent=None)
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


@pytest.mark.django_db
def test_cybersource_context(client, user):
    """The view that handles POST requests from Cybersource should add some values to the template context"""
    fake_title, fake_datetime, decision = (
        "Bootcamp Run 1",
        "2020-01-01T00:00:00Z",
        "ACCEPT",
    )
    client.force_login(user)
    url = reverse("applications")
    resp = client.get(url)
    assert "CSOURCE_PAYLOAD" in resp.context
    assert resp.context["CSOURCE_PAYLOAD"] is None
    resp = client.post(
        url,
        {
            "decision": decision,
            "signed_date_time": fake_datetime,
            "req_merchant_defined_data4": fake_title,
            "req_reference_number": "12345",
            "req_transaction_uuid": "00aa7f4ca7b440de8eb70881a58abc99",
        },
    )
    assert "CSOURCE_PAYLOAD" in resp.context
    assert json.loads(resp.context["CSOURCE_PAYLOAD"]) == {
        "decision": decision,
        "bootcamp_run_purchased": fake_title,
        "purchase_date_utc": fake_datetime,
    }


@pytest.mark.django_db
def test_cms_login_redirection(client, settings):
    """
    Test that login page of cms redirects user to login page of site
    """
    response = client.get("/cms", follow=True)
    assert response.request["PATH_INFO"] == settings.LOGIN_URL
