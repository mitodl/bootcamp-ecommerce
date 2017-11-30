"""Tests for backend related models"""
import datetime
import pytest
import pytz

from fluidreview.factories import OAuthTokenFactory

pytestmark = pytest.mark.django_db


def test_oauthtoken():
    """Test that an OAuthToken model object can be created with correct default values"""
    now = datetime.datetime.now(tz=pytz.UTC)
    token = OAuthTokenFactory.create(expires_on=now)
    assert token.expires_on == now
    assert token.token_type == 'Bearer'
