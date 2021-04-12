"""Users api"""
from collections import namedtuple
import csv
from datetime import datetime, timedelta
from functools import reduce
import logging
import re
import operator
import pytz

from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from klasses.models import BootcampRun, BootcampRunEnrollment
from main.utils import first_or_none, unique, unique_ignore_case, max_or_none
from profiles.constants import (
    ALUM_BOOTCAMP_END_DATE,
    ALUM_BOOTCAMP_NAME,
    ALUM_BOOTCAMP_RUN_TITLE,
    ALUM_BOOTCAMP_START_DATE,
    ALUM_HEADER_FIELDS,
    ALUM_LEARNER_EMAIL,
    USERNAME_MAX_LEN,
)
from profiles.exceptions import AlumImportException
from profiles.utils import usernameify

User = get_user_model()

CASE_INSENSITIVE_SEARCHABLE_FIELDS = {"email"}

Alum = namedtuple(
    "Alum",
    [
        "learner_email",
        "bootcamp_name",
        "bootcamp_run_title",
        "bootcamp_start_date",
        "bootcamp_end_date",
    ],
)
log = logging.getLogger(__name__)


def get_user_by_id(user_id):
    """
    Gets a User by id

    Args:
        user_id (int): the user id to fetch

    Returns:
        User: the user found by id
    """
    return User.objects.get(id=user_id)


def _is_case_insensitive_searchable(field_name):
    """
    Indicates whether or not a given field in the User model is a string field

    Args:
        field_name (str): The name of the User field
    Return:
        bool: True if the given User field is a string field
    """
    return field_name in CASE_INSENSITIVE_SEARCHABLE_FIELDS


def _determine_filter_field(user_property):
    """
    Assesses the value provided to search for a User and returns the field name that should
    be used for the query (e.g.: "id", "username", "email")

    Args:
        user_property (str): The id/username/email value being used to find Users
    Returns:
        str: User field name that should be used for a query based on the value provided
    """
    if isinstance(user_property, int) or user_property.isdigit():
        return "id"
    else:
        try:
            validate_email(user_property)
            return "email"
        except ValidationError:
            return "username"


def fetch_user(filter_value, ignore_case=True):
    """
    Attempts to fetch a user based on several properties

    Args:
        filter_value (Union[str, int]): The id, email, or username of some User
        ignore_case (bool): If True, the User query will be case-insensitive
    Returns:
        User: A user that matches the given property
    """
    filter_field = _determine_filter_field(filter_value)

    if _is_case_insensitive_searchable(filter_field) and ignore_case:
        query = {"{}__iexact".format(filter_field): filter_value}
    else:
        query = {filter_field: filter_value}
    try:
        return User.objects.get(**query)
    except User.DoesNotExist as e:
        raise User.DoesNotExist(
            "Could not find User with {}={} ({})".format(
                filter_field,
                filter_value,
                "case-insensitive" if ignore_case else "case-sensitive",
            )
        ) from e


def fetch_users(filter_values, ignore_case=True):
    """
    Attempts to fetch a set of users based on several properties. The property being searched
    (i.e.: id, email, or username) is assumed to be the same for all of the given values, so the
    property type is determined for the first element, then used for all of the values provided.

    Args:
        filter_values (iterable of Union[str, int]): The ids, emails, or usernames of the target Users
        ignore_case (bool): If True, the User query will be case-insensitive
    Returns:
        User queryset or None: Users that match the given properties
    """

    first_user_property = first_or_none(filter_values)
    if not first_user_property:
        return None
    filter_field = _determine_filter_field(first_user_property)
    is_case_insensitive_searchable = _is_case_insensitive_searchable(filter_field)

    unique_filter_values = set(
        unique_ignore_case(filter_values)
        if is_case_insensitive_searchable and ignore_case
        else unique(filter_values)
    )
    if len(filter_values) > len(unique_filter_values):
        raise ValidationError(
            "Duplicate values provided ({})".format(
                set(filter_values).intersection(unique_filter_values)
            )
        )

    if is_case_insensitive_searchable and ignore_case:
        query = reduce(
            operator.or_,
            (
                Q(**{"{}__iexact".format(filter_field): filter_value})
                for filter_value in filter_values
            ),
        )
        user_qset = User.objects.filter(query)
    else:
        user_qset = User.objects.filter(
            **{"{}__in".format(filter_field): filter_values}
        )
    if not user_qset.count() == len(filter_values):
        valid_values = user_qset.values_list(filter_field, flat=True)
        invalid_values = set(filter_values) - set(valid_values)
        raise User.DoesNotExist(
            "Could not find Users with these '{}' values ({}): {}".format(
                filter_field,
                "case-insensitive" if ignore_case else "case-sensitive",
                sorted(list(invalid_values)),
            )
        )
    return user_qset


def find_available_username(initial_username_base):
    """
    Returns a username with the lowest possible suffix given some base username. If the applied suffix
    makes the username longer than the username max length, characters are removed from the
    right of the username to make room.

    EXAMPLES:
    initial_username_base = "johndoe"
        Existing usernames = "johndoe"
        Return value = "johndoe1"
    initial_username_base = "johndoe"
        Existing usernames = "johndoe", "johndoe1" through "johndoe5"
        Return value = "johndoe6"
    initial_username_base = "abcdefghijklmnopqrstuvwxyz" (26 characters, assuming 26 character max)
        Existing usernames = "abcdefghijklmnopqrstuvwxyz"
        Return value = "abcdefghijklmnopqrstuvwxy1"
    initial_username_base = "abcdefghijklmnopqrstuvwxy" (25 characters long, assuming 26 character max)
        Existing usernames = "abc...y", "abc...y1" through "abc...y9"
        Return value = "abcdefghijklmnopqrstuvwx10"

    Args:
         initial_username_base (str):
    Returns:
        str: An available username
    """
    # Keeps track of the number of characters that must be cut from the username to be less than
    # the username max length when the suffix is applied.
    letters_to_truncate = 0 if len(initial_username_base) < USERNAME_MAX_LEN else 1
    # Any query for suffixed usernames could come up empty. The minimum suffix will be added to
    # the username in that case.
    current_min_suffix = 1
    while letters_to_truncate < len(initial_username_base):
        username_base = initial_username_base[
            0 : len(initial_username_base) - letters_to_truncate
        ]
        # Find usernames that match the username base and have a numerical suffix, then find the max suffix
        existing_usernames = User.objects.filter(
            username__regex=r"{username_base}[0-9]+".format(username_base=username_base)
        ).values_list("username", flat=True)
        max_suffix = max_or_none(
            int(re.search(r"\d+$", username).group()) for username in existing_usernames
        )
        if max_suffix is None:
            return "".join([username_base, str(current_min_suffix)])
        else:
            next_suffix = max_suffix + 1
            candidate_username = "".join([username_base, str(next_suffix)])
            # If the next suffix adds a digit and causes the username to exceed the character limit,
            # keep searching.
            if len(candidate_username) <= USERNAME_MAX_LEN:
                return candidate_username
        # At this point, we know there are no suffixes left to add to this username base that was tried,
        # so we will need to remove letters from the end of that username base to make room for a longer
        # suffix.
        letters_to_truncate = letters_to_truncate + 1
        available_suffix_digits = USERNAME_MAX_LEN - (
            len(initial_username_base) - letters_to_truncate
        )
        # If there is space for 4 digits for the suffix, the minimum value it could be is 1000, or 10^3
        current_min_suffix = 10 ** (available_suffix_digits - 1)


def get_first_and_last_names(user):
    """
    Returns a the most reliable values we have for a user's first and last name based on
    what they have entered for their legal address and profile.

    Args:
        user (django.contrib.auth.models.User):

    Returns:
        (str or None, str or None): A tuple containing the first name and last name, or None if those
            values could not be determined with the user information we have.
    """
    legal_address = getattr(user, "legal_address", None)
    if (
        legal_address is not None
        and legal_address.first_name
        and legal_address.last_name
    ):
        return legal_address.first_name, legal_address.last_name
    profile = getattr(user, "profile", None)
    if profile is None or not profile.name:
        return None, None
    name = profile.name or ""
    names = name.split(maxsplit=1)
    if len(names) == 0:
        return "", ""
    elif len(names) == 1:
        return names[0], ""
    else:
        return tuple(names)


def is_user_info_complete(user):
    """
    Returns True if the user has provided all of the required registration info

    Args:
        user (django.contrib.auth.models.User):

    Returns:
        bool: True if the user has provided all of the required registration info
    """
    return (
        hasattr(user, "profile")
        and user.profile.is_complete
        and hasattr(user, "legal_address")
        and user.legal_address.is_complete
    )


def import_alum(alum):
    """
    Import alum

    Args:
        alum (Alum namedtuple)
    """
    try:
        user = User.objects.get(email=alum.learner_email)
    except User.DoesNotExist:
        user = User.objects.create(
            email=alum.learner_email, username=alum.learner_email
        )

        from profiles.models import Profile, LegalAddress

        LegalAddress.objects.create(user=user)
        Profile.objects.create(user=user, can_skip_application_steps=True)
        user.username = usernameify("", user.email)
        user.save()

        log.info(
            "User does not exist against that email=%s but created without password and incomplete profile",
            alum.learner_email,
        )
    bootcamp_start_date = datetime.strptime(alum.bootcamp_start_date, "%Y-%m-%d")
    bootcamp_end_date = datetime.strptime(alum.bootcamp_end_date, "%Y-%m-%d")
    bootcamp_start_date = make_aware(bootcamp_start_date, timezone=pytz.UTC)
    bootcamp_end_date = make_aware(bootcamp_end_date, timezone=pytz.UTC)

    bootcamp_run = BootcampRun.objects.get(
        title=alum.bootcamp_run_title,
        bootcamp__title=alum.bootcamp_name,
        start_date__gte=bootcamp_start_date - timedelta(days=1),
        start_date__lte=bootcamp_start_date + timedelta(days=1),
        end_date__gte=bootcamp_end_date - timedelta(days=1),
        end_date__lte=bootcamp_end_date + timedelta(days=1),
    )

    _, created = BootcampRunEnrollment.objects.get_or_create(
        user=user, bootcamp_run=bootcamp_run
    )
    if created:
        log.info(
            "User=%s successfully enrolled in bootcamp run %s",
            alum.learner_email,
            alum.bootcamp_run_title,
        )
    else:
        log.info(
            "User=%s already exists in bootcamp run %s",
            alum.learner_email,
            alum.bootcamp_run_title,
        )


def parse_alumni_csv(csv_path):
    """
    Read CSV file and convert to Alumns object

    Args:
        csv_path(str o Path): Path to the CSV file

    Returns:
        list of Alumns, list:
    """
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)

        header_row = reader.fieldnames
        if header_row and ALUM_LEARNER_EMAIL in header_row:
            for field in ALUM_HEADER_FIELDS:
                if field not in header_row:
                    raise AlumImportException(f"Unable to find column header {field}")
        else:
            raise AlumImportException("Unable to find the header row")

        alumni = [
            Alum(
                learner_email=row[ALUM_LEARNER_EMAIL],
                bootcamp_name=row[ALUM_BOOTCAMP_NAME],
                bootcamp_run_title=row[ALUM_BOOTCAMP_RUN_TITLE],
                bootcamp_start_date=row[ALUM_BOOTCAMP_START_DATE],
                bootcamp_end_date=row[ALUM_BOOTCAMP_END_DATE],
            )
            for row in reader
        ]

        return alumni


def import_alumni(csv_path):
    """
    Import alum from the csv file

    Args:
        csv_path (str or Path): Path to a csv file
    """
    alumni = parse_alumni_csv(csv_path)

    with transaction.atomic():
        # transaction is here so, if there is a missing bootcamp and we error,
        # make sure not to not create the user as well

        for alum in alumni:
            try:
                import_alum(alum)
            except:
                raise AlumImportException(
                    f"Error while importing row for user={alum.learner_email} bootcamp={alum.bootcamp_name} run={alum.bootcamp_run_title}"
                )
