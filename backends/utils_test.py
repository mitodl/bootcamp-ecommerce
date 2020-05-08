"""
Tests for the utils
"""
from datetime import datetime, timedelta

import pytest
import pytz
from requests.exceptions import HTTPError

from backends import utils
from backends.utils import get_social_username
from backends.edxorg import EdxOrgOAuth2
# pylint: disable=protected-access


pytestmark = pytest.mark.django_db


@pytest.fixture
def now():
    """Get the time at start of test"""
    yield datetime.now(pytz.utc)


def update_social_extra_data(user, data):
    """Helper function to update the python social auth extra data"""
    social_user = user.social_auth.get(provider=EdxOrgOAuth2.name)
    social_user.extra_data.update(data)
    social_user.save()
    return social_user


@pytest.fixture
def mock_refresh(mocker, social_extra_data):
    yield mocker.patch('backends.edxorg.EdxOrgOAuth2.refresh_token', return_value=social_extra_data, autospec=True)


def test_refresh(mock_refresh, now, user):
    """The refresh needs to be called"""

    extra_data = {
        "updated_at": (now - timedelta(weeks=1)).timestamp(),
        "expires_in": 100  # seconds
    }
    social_user = update_social_extra_data(user, extra_data)
    utils.refresh_user_token(social_user)
    assert mock_refresh.called is True


def test_refresh_no_extradata(mock_refresh, user):
    """The refresh needs to be called because there is not valid timestamps"""
    social_user = user.social_auth.get(provider=EdxOrgOAuth2.name)
    social_user.extra_data = {"access_token": "fooooootoken", "refresh_token": "baaaarrefresh"}
    social_user.save()
    utils.refresh_user_token(social_user)
    assert mock_refresh.called is True


def test_no_refresh(mock_refresh, now, user):
    """The refresh does not need to be called"""
    extra_data = {
        "updated_at": (now - timedelta(minutes=1)).timestamp(),
        "expires_in": 31535999  # 1 year - 1 second
    }
    social_user = update_social_extra_data(user, extra_data)
    utils.refresh_user_token(social_user)
    assert not mock_refresh.called


def test_refresh_400_error_server(mocker, mock_refresh, user):
    """Test to check what happens when the OAUTH server returns 400 code"""
    def raise_http_error(*args, **kwargs):  # pylint: disable=unused-argument
        """Mock function to raise an exception"""
        error = HTTPError()
        error.response = mocker.MagicMock()
        error.response.status_code = 400
        raise error

    mock_refresh.side_effect = raise_http_error
    social_user = user.social_auth.get(provider=EdxOrgOAuth2.name)
    with pytest.raises(utils.InvalidCredentialStored):
        utils._send_refresh_request(social_user)


def test_refresh_401_error_server(mocker, mock_refresh, user):
    """Test to check what happens when the OAUTH server returns 401 code"""
    def raise_http_error(*args, **kwargs):  # pylint: disable=unused-argument
        """Mock function to raise an exception"""
        error = HTTPError()
        error.response = mocker.MagicMock()
        error.response.status_code = 401
        raise error

    mock_refresh.side_effect = raise_http_error
    social_user = user.social_auth.get(provider=EdxOrgOAuth2.name)
    with pytest.raises(utils.InvalidCredentialStored):
        utils._send_refresh_request(social_user)


def test_refresh_500_error_server(mocker, mock_refresh, user):
    """Test to check what happens when the OAUTH server returns 500 code"""

    def raise_http_error(*args, **kwargs):  # pylint: disable=unused-argument
        """Mock function to raise an exception"""
        error = HTTPError()
        error.response = mocker.MagicMock()
        error.response.status_code = 500
        raise error

    mock_refresh.side_effect = raise_http_error
    social_user = user.social_auth.get(provider=EdxOrgOAuth2.name)
    with pytest.raises(HTTPError):
        utils._send_refresh_request(social_user)


def test_anonymous_user(user, mocker):
    """
    get_social_username should return None for anonymous users
    """
    is_anonymous = mocker.Mock(return_value=True)
    user = mocker.Mock(is_anonymous=is_anonymous)
    assert get_social_username(user) is None


def test_zero_social(user):
    """
    get_social_username should return None if there is no edX account associated yet
    """
    user.social_auth.all().delete()
    assert get_social_username(user) is None


def test_one_social(user):
    """
    get_social_username should return the social username, not the Django username
    """
    assert get_social_username(user) == f"{user.username}_edx"
