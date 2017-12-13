"""FluidReview serializers"""
import pytz
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Serializer for FluidReview user data"""
    date_joined = serializers.DateTimeField(default_timezone=pytz.UTC, required=False)
    # FluidReview allows invalid email addresses, so use CharField instead of EmailField
    email = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True, required=False)
    full_name = serializers.CharField(allow_blank=True)
    groups = serializers.ListField(child=serializers.IntegerField(), required=False)
    id = serializers.IntegerField()
    language = serializers.CharField(required=False)
    last_login = serializers.DateTimeField(default_timezone=pytz.UTC, required=False)
    last_name = serializers.CharField(allow_null=True, required=False)
    member_of = serializers.ListField(child=serializers.IntegerField(), required=False)
    submissions = serializers.ListField(child=serializers.IntegerField(), required=False)
    teams = serializers.ListField(child=serializers.IntegerField(), required=False)
    timezone = serializers.CharField(required=False)
