"""
Serializers that are needed across all areas of the bootcamp-ecommerce application
"""
from django.core.exceptions import ObjectDoesNotExist

from backends.utils import get_social_username


def serialize_maybe_user(user):
    """
    Serialize a logged-in user to Python primitives, or an anonymous user to `None`.
    """
    if user.is_anonymous():
        return None
    try:
        full_name = user.profile.name
    except ObjectDoesNotExist:
        full_name = None
    return {
        'username': get_social_username(user),
        'full_name': full_name
    }
