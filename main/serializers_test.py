"""Tests for general bootcamp serializing functionality"""
from unittest.mock import patch, Mock
from django.test import TestCase

from profiles.factories import UserFactory, ProfileFactory
from main.serializers import serialize_maybe_user


class SerializeMaybeUserTests(TestCase):
    """Tests for serialize_maybe_user"""
    @classmethod
    def setUpTestData(cls):
        cls.profile = ProfileFactory.create(name='Full Name')

    def test_serialize_maybe_user(self):
        """Test that a user is correctly serialized"""
        with patch('main.serializers.get_social_username', return_value='abc'):
            assert serialize_maybe_user(self.profile.user) == {
                'full_name': self.profile.name,
                'username': 'abc'
            }

    def test_serialize_maybe_user_without_profile(self):
        """Test that a user without a profile is correctly serialized"""
        user_without_profile = UserFactory.create()
        with patch('main.serializers.get_social_username', return_value='abc'):
            assert serialize_maybe_user(user_without_profile) == {
                'full_name': None,
                'username': 'abc'
            }

    def test_serialize_maybe_user_anonymous(self):
        """Test that an anonymous user serializes to None"""
        is_anonymous = Mock(return_value=True)
        anon_user = Mock(is_anonymous=is_anonymous)
        assert serialize_maybe_user(anon_user) is None
