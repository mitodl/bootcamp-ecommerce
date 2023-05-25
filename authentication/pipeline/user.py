"""Auth pipline functions for user authentication"""
import json
import logging

import requests
from social_core.backends.email import EmailAuth
from social_core.exceptions import AuthException
from social_core.pipeline.partial import partial
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import reverse


from authentication.exceptions import (
    InvalidPasswordException,
    RequirePasswordException,
    RequirePasswordAndPersonalInfoException,
    RequireProfileException,
    RequireRegistrationException,
    UserCreationFailedException,
)
from authentication.utils import SocialAuthState
from authentication.api import create_user_with_generated_username

from compliance import api as compliance_api
from hubspot_sync.task_helpers import sync_hubspot_user
from profiles.serializers import UserSerializer, ProfileSerializer
from profiles.utils import usernameify

log = logging.getLogger()

NAME_MIN_LENGTH = 2

# pylint: disable=keyword-arg-before-vararg


def validate_email_auth_request(
    strategy, backend, user=None, *args, **kwargs
):  # pylint: disable=unused-argument
    """
    Validates an auth request for email

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
    """
    if backend.name != EmailAuth.name:
        return {}

    # if there's a user, force this to be a login
    if user is not None:
        return {"flow": SocialAuthState.FLOW_LOGIN}

    return {}


def get_username(
    strategy, backend, user=None, *args, **kwargs
):  # pylint: disable=unused-argument
    """
    Gets the username for a user

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
    """
    return {"username": None if not user else strategy.storage.user.get_username(user)}


@partial
def create_user_via_email(
    strategy, backend, user=None, flow=None, current_partial=None, *args, **kwargs
):  # pylint: disable=too-many-arguments,unused-argument
    """
    Creates a new user if needed and sets the password and name.
    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
        details (dict): Dict of user details
        flow (str): the type of flow (login or register)
        current_partial (Partial): the partial for the step in the pipeline

    Raises:
        RequirePasswordAndPersonalInfoException: if the user hasn't set password or name
    """
    if not strategy.is_api_enabled():
        return {}

    # if the user has data for all the fields, skip this step
    if user and user.password and user.profile.name and user.legal_address.is_complete:
        return {}

    if not strategy.is_api_request():
        return strategy.redirect_with_partial(
            reverse("signup-details"), backend.name, current_partial
        )

    data = strategy.request_data().copy()
    if data.get("profile", {}).get("name", None) is None or "password" not in data:
        raise RequirePasswordAndPersonalInfoException(backend, current_partial)
    if len(data.get("profile", {}).get("name", 0)) < NAME_MIN_LENGTH:
        raise RequirePasswordAndPersonalInfoException(
            backend,
            current_partial,
            errors=["Full name must be at least 2 characters long."],
        )

    data["email"] = kwargs.get("email", kwargs.get("details", {}).get("email"))

    is_new = user is None

    if is_new:
        username = usernameify(data["profile"]["name"], email=data["email"])
        data["username"] = username
        serializer = UserSerializer(data=data)
    else:
        serializer = UserSerializer(user, data=data)

    if not serializer.is_valid():
        raise RequirePasswordAndPersonalInfoException(
            backend, current_partial, errors=serializer.errors
        )

    if is_new:
        try:
            user = create_user_with_generated_username(serializer, username)
            if user is None:
                raise IntegrityError(
                    "Failed to create User with generated username ({})".format(
                        username
                    )
                )
        except Exception as exc:
            raise UserCreationFailedException(backend, current_partial) from exc
    else:
        user = serializer.save()
    return {"is_new": is_new, "user": user, "username": user.username}


@partial
def create_profile(
    strategy, backend, user=None, flow=None, current_partial=None, *args, **kwargs
):  # pylint: disable=too-many-arguments,unused-argument
    """
    Creates a new profile for the user
    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
        flow (str): the type of flow (login or register)
        current_partial (Partial): the partial for the step in the pipeline

    Raises:
        RequireProfileException: if the profile data is missing or invalid
    """
    if user.profile.is_complete or not strategy.is_api_enabled():
        return {}

    if not strategy.is_api_request():
        return strategy.redirect_with_partial(
            reverse("signup-extra"), backend.name, current_partial
        )

    data = strategy.request_data().copy()

    serializer = ProfileSerializer(instance=user.profile, data=data)
    if not serializer.is_valid():
        raise RequireProfileException(
            backend, current_partial, errors=serializer.errors
        )
    serializer.save()
    sync_hubspot_user(user)
    return {}


@partial
def validate_password(
    strategy, backend, user=None, flow=None, current_partial=None, *args, **kwargs
):  # pylint: disable=unused-argument
    """
    Validates a user's password for login

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
        flow (str): the type of flow (login or register)
        current_partial (Partial): the partial for the step in the pipeline

    Raises:
        RequirePasswordException: if the user password is invalid
    """
    if backend.name != EmailAuth.name or flow != SocialAuthState.FLOW_LOGIN:
        return {}

    data = strategy.request_data()

    if user is None:
        raise RequireRegistrationException(backend, current_partial)

    if "password" not in data:
        raise RequirePasswordException(backend, current_partial)

    password = data["password"]

    if not user or not user.check_password(password):
        raise InvalidPasswordException(backend, current_partial)

    return {}


def forbid_hijack(strategy, backend, **kwargs):  # pylint: disable=unused-argument
    """
    Forbid an admin user from trying to login/register while hijacking another user

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
    """
    # As first step in pipeline, stop a hijacking admin from going any further
    if strategy.session_get("is_hijacked_user"):
        raise AuthException("You are hijacking another user, don't try to login again")
    return {}


def activate_user(
    strategy, backend, user=None, is_new=False, **kwargs
):  # pylint: disable=unused-argument
    """
    Activate the user's account if they passed export controls

    Args:
        strategy (social_django.strategy.DjangoStrategy): the strategy used to authenticate
        backend (social_core.backends.base.BaseAuth): the backend being used to authenticate
        user (User): the current user
    """
    if user.is_active or not strategy.is_api_enabled():
        return {}

    export_inquiry = compliance_api.get_latest_exports_inquiry(user)

    # if the user has an export inquiry that is considered successful, activate them
    if not compliance_api.is_exports_verification_enabled() or (
        export_inquiry is not None and export_inquiry.is_success
    ):
        user.is_active = True
        user.save()

    return {}


def send_user_to_hubspot(request, **kwargs):
    """
    Create a hubspot contact using the hubspot Forms API
    Submit the user's email and optionally a hubspotutk cookie
    """
    portal_id = settings.HUBSPOT_CONFIG.get("HUBSPOT_PORTAL_ID")
    form_id = settings.HUBSPOT_CONFIG.get("HUBSPOT_CREATE_USER_FORM_ID")

    if not (portal_id and form_id):
        log.error(
            "HUBSPOT_PORTAL_ID or HUBSPOT_CREATE_USER_FORM_ID not set. Can't submit to Hubspot forms api."
        )
        return {}

    hutk = request.COOKIES.get("hubspotutk")
    email = kwargs.get("email", kwargs.get("details", {}).get("email"))

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    data = {"email": email}

    if hutk:
        data["hs_context"] = json.dumps({"hutk": hutk})

    url = f"https://forms.hubspot.com/uploads/form/v2/{portal_id}/{form_id}?&"

    requests.post(url=url, data=data, headers=headers)

    return {}

def sync_user_profile_to_hubspot(
    backend, user, response, is_new, *args, **kwargs
):  # pylint: disable=unused-argument
    """
    Sync the user's latest profile data with hubspot on login
    """
    sync_hubspot_user(user)
