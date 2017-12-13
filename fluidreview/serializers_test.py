"""fluidreview serializer tests"""
from fluidreview import serializers


def test_user_serializer():
    """Tests for the fluidreview user serializer"""
    user_data = {
        'date_joined': '2017-11-21T21:30:54',
        'email': 'fakeapplicant@mit.edu',
        'first_name': 'Fake" ,;\\n',
        'full_name': 'Fake" ,;\\n Applicant" ;,',
        'groups': [49225],
        'id': 95195890,
        'language': 'en',
        'last_login': '2017-11-29T17:17:57',
        'last_name': 'Applicant" ;,',
        'member_of': [],
        'submissions': [4446598, 4446700],
        'teams': [],
        'timezone': 'US/Eastern'
    }
    serializer = serializers.UserSerializer(data=user_data)
    assert serializer.is_valid()


def test_user_serializer_not_found():
    """Test that a Fluid Review response for a nonexistent user doesn't pass serializer validation"""
    user_data = {
        'detail': 'Not found.',
        'status_code': 404
    }
    serializer = serializers.UserSerializer(data=user_data)
    assert serializer.is_valid() is False
