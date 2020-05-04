"""User app utility functions"""
import logging
import re

from django.contrib.auth import get_user_model

from profiles.constants import USERNAME_MAX_LEN

User = get_user_model()
log = logging.getLogger(__name__)

USERNAME_SEPARATOR = "-"
# Characters that should be replaced by the specified separator character
USERNAME_SEPARATOR_REPLACE_CHARS = "\\s_"
# Characters that should be removed entirely from the full name to create the username
USERNAME_INVALID_CHAR_PATTERN = r"[^\w{}{}]|[\d]".format(
    USERNAME_SEPARATOR_REPLACE_CHARS, USERNAME_SEPARATOR
)

USERNAME_TURKISH_I_CHARS = r"[ıİ]"
USERNAME_TURKISH_I_CHARS_REPLACEMENT = "i"

# Pattern for chars to replace with a single separator. The separator character itself
# is also included in this pattern so repeated separators are squashed down.
USERNAME_SEPARATOR_REPLACE_PATTERN = r"[{}{}]+".format(
    USERNAME_SEPARATOR_REPLACE_CHARS, USERNAME_SEPARATOR
)


def _reformat_for_username(string):
    """
    Removes/substitutes characters in a string to make it suitable as a username value

    Args:
        string (str): A string
    Returns:
        str: A version of the string with username-appropriate characters
    """
    cleaned_string = re.sub(USERNAME_INVALID_CHAR_PATTERN, "", string)
    cleaned_string = re.sub(
        USERNAME_TURKISH_I_CHARS, USERNAME_TURKISH_I_CHARS_REPLACEMENT, cleaned_string
    )
    return (
        re.sub(USERNAME_SEPARATOR_REPLACE_PATTERN, USERNAME_SEPARATOR, cleaned_string)
        .lower()
        .strip(USERNAME_SEPARATOR)
    )


def usernameify(full_name, email=""):
    """
    Generates a username based on a full name, or an email address as a fallback.

    Args:
        full_name (str): A full name (i.e.: User.name)
        email (str): An email address to use as a fallback if the full name produces
            a blank username
    Returns:
        str: A generated username
    Raises:
        ValueError: Raised if generated username was blank after trying both the
            full name and email
    """
    username = _reformat_for_username(full_name)

    if not username and email:
        log.error(
            "User's full name could not be used to generate a username (full name: '%s'). "
            "Trying email instead...",
            full_name,
        )
        username = _reformat_for_username(email.split("@")[0])
    if not username:
        raise ValueError(
            "Username could not be generated (full_name: '{}', email: '{}')".format(
                full_name, email
            )
        )
    return username[0:USERNAME_MAX_LEN]


def is_duplicate_username_error(exc):
    """
    Returns True if the given exception indicates that there was an attempt to save a User record with an
    already-existing username.

    Args:
        exc (Exception): An exception

    Returns:
        bool: Whether or not the exception indicates a duplicate username error
    """
    return re.search(r"\(username\)=\([^\s]+\) already exists", str(exc)) is not None


def ensure_active_user(user):
    """
    Activates the user (if required)

    Args:
        user (User): The user to activate/verify as functional
    """
    if not user.is_active:
        user.is_active = True
        user.save()
        log.info("User %s activated", user.email)
