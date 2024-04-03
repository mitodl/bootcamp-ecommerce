"""jobma tests for permissions"""

from django.http.request import HttpHeaders
from jobma.permissions import JobmaWebhookPermission


def test_webhook_auth(settings, mocker):
    """The permission check should pass if the auth token matches"""
    token = "asdfghjk"
    settings.JOBMA_WEBHOOK_ACCESS_TOKEN = token
    request = mocker.Mock(
        headers=HttpHeaders({"HTTP_AUTHORIZATION": f"Bearer {token}"})
    )
    assert JobmaWebhookPermission().has_permission(request, mocker.Mock()) is True


def test_webhook_auth_incorrect(settings, mocker):
    """If the token doesn't match, it should not have permission"""
    token = "asdfghjk"
    settings.JOBMA_WEBHOOK_ACCESS_TOKEN = token
    request = mocker.Mock(
        headers=HttpHeaders({"HTTP_AUTHORIZATION": "Bearer someothertoken"})
    )
    assert JobmaWebhookPermission().has_permission(request, mocker.Mock()) is False


def test_webhook_auth_missing(mocker):
    """If there is no header, it should not have permission"""
    request = mocker.Mock(headers=HttpHeaders({}))
    assert JobmaWebhookPermission().has_permission(request, mocker.Mock()) is False
