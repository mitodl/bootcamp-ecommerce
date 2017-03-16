"""
Utility functions for the backends
"""
from datetime import datetime, timedelta
import logging
import pytz

from django.core.exceptions import ObjectDoesNotExist
from requests.exceptions import HTTPError
from social_django.utils import load_strategy

from backends.exceptions import InvalidCredentialStored
from backends.edxorg import EdxOrgOAuth2


log = logging.getLogger(__name__)


def _send_refresh_request(user_social):
    """
    Private function that refresh an user access token
    """
    strategy = load_strategy()
    try:
        user_social.refresh_token(strategy)
    except HTTPError as exc:
        if exc.response.status_code in (400, 401,):
            raise InvalidCredentialStored(
                message='Received a {} status code from the OAUTH server'.format(
                    exc.response.status_code),
                http_status_code=exc.response.status_code
            )
        raise


def refresh_user_token(user_social):
    """
    Utility function to refresh the access token if is (almost) expired

    Args:
        user_social (UserSocialAuth): a user social auth instance
    """
    try:
        last_update = datetime.fromtimestamp(user_social.extra_data.get('updated_at'), tz=pytz.UTC)
        expires_in = timedelta(seconds=user_social.extra_data.get('expires_in'))
    except TypeError:
        _send_refresh_request(user_social)
        return
    # small error margin of 5 minutes to be safe
    error_margin = timedelta(minutes=5)
    if datetime.now(tz=pytz.UTC) - last_update >= expires_in - error_margin:
        _send_refresh_request(user_social)


def split_name(name):
    """
    Split a name into two names. If there is only one name, the last name will be
    empty. If there are more than two, the extra names will be appended to the last
    name.

    Args:
        name (str): A name to split into first name, last name
    Returns:
        tuple: (first, last)
    """
    if name is None:
        return "", ""
    names = name.split(maxsplit=1)
    if len(names) == 0:
        return "", ""
    else:
        return names[0], " ".join(names[1:])


def split_and_truncate_name(name):
    """
    Split a name into two names and truncate each name to fit within 30 character limit in User object.

    Args:
        name (str): A name to split into first name, last name
    Returns:
        tuple: (first, last)
    """
    first, last = split_name(name)
    return first[:30], last[:30]


def get_social_username(user):
    """
    Get social auth edX username for a user, or else return None.

    Args:
        user (django.contrib.auth.models.User):
            A Django user
    """
    if user.is_anonymous():
        return None

    try:
        return user.social_auth.get(provider=EdxOrgOAuth2.name).uid
    except ObjectDoesNotExist:
        return None
    except Exception as ex:  # pylint: disable=broad-except
        log.error("Unexpected error retrieving social auth username: %s", ex)
        return None
