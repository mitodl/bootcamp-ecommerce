"""Tests for FluidReview views"""
import pytest
from django.core.urlresolvers import reverse
from rest_framework import status

from fluidreview.models import WebhookRequest


@pytest.mark.parametrize("data", ['', "some data", '{"json": "body"}'])
def test_webhook(db, data, client, settings):  # pylint: disable=unused-argument
    """
    The fluidreview webhook should store its data in the WebhookRequest model, no matter what the data is
    """
    token = 'zxvbnm'

    settings.FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = token
    url = reverse('fluidreview-webhook')
    resp = client.post(url, data=data, HTTP_AUTHORIZATION="Basic {}".format(token), content_type="text/plain")
    assert resp.status_code == status.HTTP_200_OK
    assert WebhookRequest.objects.count() == 1
    assert WebhookRequest.objects.first().body == data


@pytest.mark.parametrize("token_missing", [True, False])
def test_webhook_fail_auth(db, client, settings, token_missing):  # pylint: disable=unused-argument
    """
    If the token doesn't match we should return a 403 and not record the webhook
    """
    headers = {}
    settings.FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = 'xyz'
    if not token_missing:
        headers['HTTP_AUTHORIZATION'] = 'Basic abc'

    url = reverse('fluidreview-webhook')
    resp = client.post(url, data="body", content_type="text/plain", **headers)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert WebhookRequest.objects.count() == 0
