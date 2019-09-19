"""Serializers for smapply"""
from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    """Serializer for SMApply user data"""
    email = serializers.CharField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    id = serializers.IntegerField()
