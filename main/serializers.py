"""
Serializers that are needed across all areas of the bootcamp-ecommerce application
"""
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from backends.utils import get_social_username


def serialize_maybe_user(user):
    """
    Serialize a logged-in user to Python primitives, or an anonymous user to `None`.
    """
    if user.is_anonymous:
        return None
    try:
        full_name = user.profile.name.strip()
    except ObjectDoesNotExist:
        full_name = None
    return {"username": get_social_username(user), "full_name": full_name}


class WriteableSerializerMethodField(serializers.SerializerMethodField):
    """
    A SerializerMethodField which has been marked as not read_only so that submitted data passed validation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.read_only = False

    def to_internal_value(self, data):
        return data
