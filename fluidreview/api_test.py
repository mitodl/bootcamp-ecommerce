"""
FluidReview Backend Tests
"""
import datetime

import pytest
from django.test import override_settings

from fluidreview.factories import OAuthTokenFactory
from fluidreview.api import FluidReviewAPI, BASE_API_URL
from fluidreview.models import OAuthToken
from fluidreview.utils import utc_now

pytestmark = pytest.mark.django_db


def test_get_token_from_settings(settings):
    """ Test that the FluidReviewAPI instance token is initially based off settings"""
    settings.FLUIDREVIEW_ACCESS_TOKEN = 'fakeaccesstoken'
    settings.FLUIDREVIEW_REFRESH_TOKEN = 'fakerefreshtoken'
    frapi = FluidReviewAPI()
    token = frapi.get_token()
    assert token['access_token'] == settings.FLUIDREVIEW_ACCESS_TOKEN
    assert token['refresh_token'] == settings.FLUIDREVIEW_REFRESH_TOKEN


def test_get_token_from_database():
    """ Test that a FluidReviewAPI instance token is retrieved from the database if it exists"""
    dbtoken = OAuthTokenFactory(expires_on=utc_now())
    frapi = FluidReviewAPI()
    token = frapi.get_token()
    assert token['access_token'] == dbtoken.access_token
    assert token['refresh_token'] == dbtoken.refresh_token


def test_save_token_new():
    """Test that the save_token method correctly creates a new OAuthToken in the database"""
    assert OAuthToken.objects.first() is None
    response_token = {
        'access_token': 'fakeaccesstoken',
        'refresh_token': 'fakerefreshtoken',
        'expires_in': 1000,
        'token_type': 'faketype'
    }
    frapi = FluidReviewAPI()
    now = utc_now()
    new_token = frapi.save_token(response_token)
    for attr in ['access_token', 'refresh_token', 'token_type']:
        assert response_token[attr] == getattr(new_token, attr)
        assert response_token[attr] == new_token.json[attr]
    # Ensure expires_on, expires_in values are close to expected value
    assert now + datetime.timedelta(seconds=985) <= new_token.expires_on <= now + datetime.timedelta(seconds=1000)
    assert 985 <= new_token.json['expires_in'] < 1000


def test_save_token_update():
    """Test that the save_token method correctly updates an existing OAuthToken in the database"""
    initial_token = OAuthTokenFactory(
        expires_on=utc_now() - datetime.timedelta(seconds=7200),
        access_token='oldaccess',
        refresh_token='oldrefresh'
    )
    response_token = {
        'access_token': 'fakeaccesstoken',
        'refresh_token': 'fakerefreshtoken',
        'expires_in': 7200,
        'token_type': 'faketype'
    }
    base_attrs = ['access_token', 'refresh_token', 'token_type']
    frapi = FluidReviewAPI()
    for attr in base_attrs:
        assert getattr(initial_token, attr) == frapi.session.token[attr]
    frapi.save_token(response_token)
    frapi.session = frapi.initialize_session()
    for attr in base_attrs:
        assert response_token[attr] == frapi.session.token[attr]
    # Ensure expires_in is close to expected value
    assert 7185 <= frapi.session.token['expires_in'] <= 7200


@override_settings(FLUIDREVIEW_BASE_URL="http://test.bootcamp.zzz")
@pytest.mark.parametrize(['method', 'url', 'full_url', 'kwargs'], [
    ['get', 'users', '{}users', {}],
    ['get', '/users', '{}users', {}],
    ['get', '/users?testing=true', '{}users?testing=true', {}],
    ['put', 'installments/2', '{}installments/2', {'data': {'transaction': 1}}],
    ['post', 'transactions', '{}transactions', {'data': {'application': 3}}]
])
def test_oauth_requests(mocker, method, url, full_url, kwargs):
    """Test that OAuth2Session calls the correct request method with correct arguments"""
    mock_oauth = mocker.patch('fluidreview.api.OAuth2Session.{}'.format(method))
    FluidReviewAPI().request(method, url, **kwargs)
    mock_oauth.assert_called_once_with(full_url.format(BASE_API_URL), **kwargs)


@pytest.mark.parametrize(['method', 'url', 'kwargs'], [
    ['get', 'users', {}],
    ['put', 'installments/2', {'data': {'transaction': 1}}],
    ['post', 'transactions', {'data': {'application': 3}}]
])
def test_api_requests(mocker, method, url, kwargs):
    """Test that FluidReviewAPI.request method gets called with the correct arguments"""
    mock_request = mocker.patch('fluidreview.api.FluidReviewAPI.request')
    frapi = FluidReviewAPI()
    getattr(frapi, method)(url, **kwargs)
    mock_request.assert_called_once_with(method, url, **kwargs)


def test_api_request_invalid_token(mocker):
    """Test that a request will be tried 2x and the session reinitialized if the tokens are no longer valid"""
    mock_session = mocker.patch('fluidreview.api.OAuth2Session')
    mock_init = mocker.patch('fluidreview.api.FluidReviewAPI.initialize_session', return_value=mock_session)
    mock_session.get.return_value.status_code = 401
    frapi = FluidReviewAPI()
    frapi.get('users')
    assert mock_session.get.call_count == 2
    assert mock_init.call_count == 2
