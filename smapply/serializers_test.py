"""Tests for smapply serializers"""
from smapply import serializers


def test_user_serializer():
    """Tests for the smapply user serializer"""
    user_data = {
        'id': 12345678,
        'first_name': 'first_name',
        'last_name': 'last_name',
        'email': 'test1@test.co'
    }
    serializer = serializers.UserSerializer(data=user_data)
    assert serializer.is_valid()


def test_user_serializer_not_found():
    """Test that a smapply UserSerializer properly rejects bad data"""
    user_data = {
        'bad_data': 'bad_data',
    }
    serializer = serializers.UserSerializer(data=user_data)
    assert serializer.is_valid() is False
