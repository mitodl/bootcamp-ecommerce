"""Tests for general bootcamp serializing functionality"""
import pytest

from profiles.factories import UserFactory, ProfileFactory
from main.serializers import serialize_maybe_user


pytestmark = pytest.mark.django_db


@pytest.fixture
def profile():
    """Make a profile for testing"""
    yield ProfileFactory.create(name='Full Name')


# pylint: disable=redefined-outer-name,unused-argument
def test_serialize_maybe_user(mocker, profile):
    """Test that a user is correctly serialized"""
    mocker.patch('main.serializers.get_social_username', return_value='abc')
    assert serialize_maybe_user(profile.user) == {
        'full_name': profile.name,
        'username': 'abc'
    }


def test_serialize_maybe_user_without_profile(mocker, profile):
    """Test that a user without a profile is correctly serialized"""
    user_without_profile = UserFactory.create(profile=None)
    mocker.patch('main.serializers.get_social_username', return_value='abc')
    assert serialize_maybe_user(user_without_profile) == {
        'full_name': None,
        'username': 'abc'
    }


def test_serialize_maybe_user_anonymous(mocker):
    """Test that an anonymous user serializes to None"""
    is_anonymous = mocker.Mock(return_value=True)
    anon_user = mocker.Mock(is_anonymous=is_anonymous)
    assert serialize_maybe_user(anon_user) is None
