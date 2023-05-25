"""
APIs for extending the python social auth pipeline
"""
import logging
from datetime import datetime
from urllib.parse import urljoin

import pytz

from backends.edxorg import EdxOrgOAuth2
from backends.utils import get_social_username
from hubspot_sync.task_helpers import sync_hubspot_user
from profiles.models import Profile

log = logging.getLogger(__name__)


def update_profile_from_edx(
    backend, user, response, is_new, *args, **kwargs
):  # pylint: disable=unused-argument
    """
    Gets profile information from edX and saves it in the Profile object (creating one if necessary)

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

    access_token = response.get("access_token")
    if not access_token:
        # this should never happen for the edx oauth provider, but just in case...
        log.error("Missing access token for the user %s", user.username)
        return

    username = get_social_username(user)
    user_profile_edx = backend.get_json(
        urljoin(backend.EDXORG_BASE_URL, "/api/user/v1/accounts/{0}".format(username)),
        headers={"Authorization": "Bearer {}".format(access_token)},
    )

    # update email anyway.
    update_email(user_profile_edx, user)
    if not is_new:
        return

    # for new users
    profile, _ = Profile.objects.get_or_create(user=user)
    name = user_profile_edx.get("name", "")
    profile.name = name
    profile.save()

    log.debug(
        'Profile for user "%s" updated with values from EDX %s',
        user.username,
        user_profile_edx,
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
    details["updated_at"] = datetime.now(tz=pytz.UTC).timestamp()
    return details


def update_email(user_profile_edx, user):
    """
    updates email address of user
    Args:
        user_profile_edx (dict): user details from edX
        user (User): user object
    """
    user.email = user_profile_edx.get("email")
    user.save()
