"""Tests for FluidReview views"""
import json
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status

from fluidreview.models import WebhookRequest
from klasses.factories import KlassFactory
from profiles.factories import ProfileFactory
from profiles.models import Profile

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("data", ['', "some data", '{"json": "body"}'])
def test_webhook(data, client, settings, mocker):  # pylint: disable=unused-argument
    """
    The fluidreview webhook should store its data in the WebhookRequest model, no matter what the data is
    """
    mocker.patch('fluidreview.api.FluidReviewAPI')
    token = 'zxvbnm'
    settings.FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = token
    url = reverse('fluidreview-webhook')
    resp = client.post(url, data=data, HTTP_AUTHORIZATION='Basic {}'.format(token), content_type='text/plain')
    assert resp.status_code == status.HTTP_200_OK
    assert WebhookRequest.objects.count() == 1
    assert WebhookRequest.objects.first().body == data


@pytest.mark.parametrize("token_missing", [True, False])
def test_webhook_fail_auth(client, settings, token_missing, mocker):  # pylint: disable=unused-argument
    """
    If the token doesn't match we should return a 403 and not record the webhook
    """
    mocker.patch('fluidreview.api.FluidReviewAPI')
    headers = {}
    settings.FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = 'xyz'
    if not token_missing:
        headers['HTTP_AUTHORIZATION'] = 'Basic abc'

    url = reverse('fluidreview-webhook')
    resp = client.post(url, data='body', content_type='text/plain', **headers)
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert WebhookRequest.objects.count() == 0


@pytest.mark.parametrize(["email", "fluid_id", "should_update"], [
    ['new@mit.edx', 95195890, True],
    ['old@mit.edx', 95195891, True],
    ['old@mit.edx', 95195892, False]
])  # pylint: disable=too-many-arguments,too-many-locals
def test_webhook_parse_success(email, fluid_id, should_update, settings, client, mocker):
    """
    The webhook request body should be successfully parsed into separate fields, and user/profile created if necessary
    """
    user_data = {
        'date_joined': '2017-11-21T21:30:54',
        'email': email,
        'first_name': 'Fake',
        'full_name': 'Fake Applicant {}'.format(fluid_id),
        'groups': [],
        'id': fluid_id,
        'language': 'en',
        'last_login': '2017-11-29T17:17:57',
        'last_name': 'Applicant',
        'member_of': [],
        'submissions': [],
        'teams': [],
    }
    mock_api = mocker.patch('fluidreview.api.FluidReviewAPI')
    mock_api().get.return_value.json.return_value = user_data

    existing_user = 'old@mit.edx'
    ProfileFactory.create(
        user__email=existing_user,
        fluidreview_id=None if should_update else fluid_id
    )
    KlassFactory.create(klass_key=81265)
    data = {
        'date_of_birth': '',
        'user_email': email,
        'amount_to_pay': '',
        'user_id': fluid_id,
        'submission_id': 4533767,
        'award_id': 81265,
        'award_cost': '1000',
        'award_name': 'TEST CAMP'
    }
    body = json.dumps(data)

    token = 'zxvbnm'
    settings.FLUIDREVIEW_WEBHOOK_AUTH_TOKEN = token
    url = reverse('fluidreview-webhook')
    resp = client.post(url, data=body, HTTP_AUTHORIZATION='Basic {}'.format(token), content_type='text/plain')
    assert resp.status_code == status.HTTP_200_OK

    webhook = WebhookRequest.objects.get(body=body)
    for attr in ('user_email', 'user_id', 'submission_id', 'award_id', 'award_name'):
        assert getattr(webhook, attr) == data[attr]
    assert webhook.award_cost == Decimal(data['award_cost'])
    assert webhook.amount_to_pay is None

    req_profile = Profile.objects.get(fluidreview_id=data['user_id'])
    assert should_update is (req_profile.name == user_data['full_name'])
    assert req_profile.user == User.objects.get(email=email)
