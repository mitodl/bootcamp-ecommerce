"""
APIs for extending the python social auth pipeline
"""
import logging
from datetime import datetime
from urllib.parse import urljoin

import pytz

from backends.edxorg import EdxOrgOAuth2
from backends.utils import (
    get_social_username,
    split_and_truncate_name,
)

log = logging.getLogger(__name__)


def update_user_from_edx(backend, user, response, is_new, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Gets profile information from edX and saves it in the User object

    Args:
        backend (social.backends.oauth.BaseOAuth2): the python social auth backend
        user (User): user object
        response (dict): dictionary of the user information coming
            from previous functions in the pipeline
        is_new (bool): whether the authenticated user created a new local instance

    Returns:
        None
    """
    if backend.name != EdxOrgOAuth2.name:
        return

    # We don't check is_new here because something else in the pipeline is updating the User
    # and we need to fix it here

    access_token = response.get('access_token')
    if not access_token:
        # this should never happen for the edx oauth provider, but just in case...
        log.error('Missing access token for the user %s', user.username)
        return

    username = get_social_username(user)
    user_profile_edx = backend.get_json(
        urljoin(backend.EDXORG_BASE_URL, '/api/user/v1/accounts/{0}'.format(username)),
        headers={
            "Authorization": "Bearer {}".format(access_token),
        }
    )
    name = user_profile_edx.get('name', '')
    user.first_name, user.last_name = split_and_truncate_name(name)
    user.save()

    log.debug(
        'Profile for user "%s" updated with values from EDX %s',
        user.username,
        user_profile_edx
    )


def set_last_update(details, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Pipeline function to add extra information about when the social auth
    profile has been updated.

    Args:
        details (dict): dictionary of informations about the user

    Returns:
        dict: updated details dictionary
    """
    details['updated_at'] = datetime.now(tz=pytz.UTC).timestamp()
    return details
