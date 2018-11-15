"""Tests for FluidReview views"""
import json

import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status

from smapply.api import SMApplyException
from smapply.models import WebhookRequestSMA
from klasses.factories import KlassFactory
from profiles.factories import ProfileFactory
from profiles.models import Profile

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("data", ['', "some data", '{"json": "body"}'])
def test_webhook(data, client, settings, mocker):  # pylint: disable=unused-argument
    """
    The fluidreview webhook should store its data in the WebhookRequest model, no matter what the data is
    """
    mocker.patch('smapply.api.SMApplyAPI')
    token = 'zxvbnm'
    settings.SMAPPLY_WEBHOOK_AUTH_TOKEN = token
    url = reverse('smapply-webhook')
    resp = client.post(url, data=data, HTTP_AUTHORIZATION='OAuth {}'.format(token), content_type='text/plain')
    assert resp.status_code == status.HTTP_200_OK
    assert WebhookRequestSMA.objects.count() == 1
    assert WebhookRequestSMA.objects.first().body == data


@pytest.mark.parametrize("token_missing", [True, False])
def test_webhook_fail_auth(client, settings, token_missing, mocker):  # pylint: disable=unused-argument
    """
    If the token doesn't match we should return a 403 and not record the webhook
    """
    mocker.patch('smapply.api.SMApplyAPI')
    headers = {}
    settings.SMAPPLY_WEBHOOK_AUTH_TOKEN = 'xyz'
    if not token_missing:
        headers['HTTP_AUTHORIZATION'] = 'OAuth abc'

    url = reverse('smapply-webhook')
    with pytest.raises(SMApplyException) as exc:
        client.post(url, data='body', content_type='text/plain', **headers)
    assert 'You do not have permission' in str(exc.value)
    assert WebhookRequestSMA.objects.count() == 0


@pytest.mark.parametrize("accept", ["text/plain", "application/json", "video/mp4", "foo", "", None])
def test_webhook_with_accept_header(client, settings, mocker, accept):  # pylint: disable=unused-argument
    """
    Return a valid response no matter what the 'Accept' header is.
    """
    mocker.patch('smapply.api.SMApplyAPI')
    settings.SMAPPLY_WEBHOOK_AUTH_TOKEN = 'xyz'
    headers = {
        'HTTP_AUTHORIZATION': 'OAuth xyz'
    }
    if accept is not None:
        headers['HTTP_ACCEPT'] = accept
    url = reverse('smapply-webhook')
    resp = client.post(url, data='body', content_type='text/plain', **headers)
    assert resp.status_code == status.HTTP_200_OK
    assert WebhookRequestSMA.objects.count() == 1


@pytest.mark.parametrize(["email", "smapply_id", "should_update"], [
    ['new@mit.edx', 95195890, True],
    ['old@mit.edx', 95195891, True],
    ['old@mit.edx', 95195892, False]
])  # pylint: disable=too-many-arguments,too-many-locals
def test_webhook_parse_success(email, smapply_id, should_update, settings, client, mocker):
    """
    The webhook request body should be successfully parsed into separate fields, and user/profile created if necessary
    """
    user_data = {
        'date_joined': '2017-11-21T21:30:54',
        'email': email,
        'first_name': 'Fake',
        'full_name': 'Fake Applicant {}'.format(smapply_id),
        'groups': [],
        'id': smapply_id,
        'language': 'en',
        'last_login': '2017-11-29T17:17:57',
        'last_name': 'Applicant',
        'member_of': [],
        'submissions': [],
        'teams': [],
    }
    mock_api = mocker.patch('smapply.api.SMApplyAPI')
    mock_api().get.return_value.json.return_value = user_data

    existing_user = 'old@mit.edx'
    ProfileFactory.create(
        user__email=existing_user,
        smapply_id=None if should_update else smapply_id
    )
    KlassFactory.create(klass_key=81265)
    data = {
        'user_id': smapply_id,
        'id': 4533768,
        'award': 81265,
    }
    body = json.dumps(data)

    token = 'zxvbnm'
    settings.SMAPPLY_WEBHOOK_AUTH_TOKEN = token
    url = reverse('smapply-webhook')
    resp = client.post(url, data=body, HTTP_AUTHORIZATION='OAuth {}'.format(token), content_type='text/plain')
    assert resp.status_code == status.HTTP_200_OK

    webhook = WebhookRequestSMA.objects.filter(body=body).first()
    assert webhook.user_id == data['user_id']

    req_profile = Profile.objects.get(smapply_id=data['user_id'])
    assert should_update is (req_profile.name == user_data['full_name'])
    assert req_profile.user == User.objects.get(email=email)
