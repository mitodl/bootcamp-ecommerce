"""
Models classes needed for bootcamp
"""

import uuid
from datetime import timedelta

import pycountry
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mitol.common.models import TimestampedModel
from mitol.common.utils import now_in_utc

from main.utils import is_blank
from profiles import api as profile_api
from profiles.constants import (
    COMPANY_SIZE_CHOICES,
    COUNTRIES_REQUIRING_POSTAL_CODE,
    GENDER_CHOICES,
    HIGHEST_EDUCATION_CHOICES,
    YRS_EXPERIENCE_CHOICES,
)


def generate_change_email_code():
    """Generates a new change email code"""
    return uuid.uuid4().hex


def generate_change_email_expires():
    """Generates the expiry datetime for a change email request"""
    return now_in_utc() + timedelta(minutes=settings.AUTH_CHANGE_EMAIL_TTL_IN_MINUTES)


class ChangeEmailRequest(TimestampedModel):
    """Model for tracking an attempt to change the user's email"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="change_email_attempts",
    )
    new_email = models.EmailField(blank=False)

    code = models.CharField(
        unique=True, blank=False, default=generate_change_email_code, max_length=32
    )
    confirmed = models.BooleanField(default=False)
    expires_on = models.DateTimeField(default=generate_change_email_expires)

    class Meta:
        index_together = ("expires_on", "confirmed", "code")


def validate_iso_3166_1_code(value):
    """
    Verify the value is a known subdivision

    Args:
        value (str): the code value

    Raises:
        ValidationError: raised if not a valid code
    """
    if pycountry.countries.get(alpha_2=value) is None:
        raise ValidationError(
            _("%(value)s is not a valid ISO 3166-1 country code"),
            params={"value": value},
        )


def validate_iso_3166_2_code(value):
    """
    Verify the value is a known subdivision

    Args:
        value (str): the code value

    Raises:
        ValidationError: raised if not a valid code
    """
    if pycountry.subdivisions.get(code=value) is None:
        raise ValidationError(
            _("%(value)s is not a valid ISO 3166-2 subdivision code"),
            params={"value": value},
        )


class LegalAddress(TimestampedModel):
    """A user's legal address, used for SDN compliance"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="legal_address"
    )

    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)

    street_address_1 = models.CharField(max_length=60, blank=True)
    street_address_2 = models.CharField(max_length=60, blank=True)
    street_address_3 = models.CharField(max_length=60, blank=True)
    street_address_4 = models.CharField(max_length=60, blank=True)
    street_address_5 = models.CharField(max_length=60, blank=True)

    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(
        max_length=2, blank=True, validators=[validate_iso_3166_1_code]
    )  # ISO-3166-1

    # only required in the US/CA
    state_or_territory = models.CharField(
        max_length=6, blank=True, validators=[validate_iso_3166_2_code]
    )  # ISO 3166-2
    postal_code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        """Str representation for the legal address"""
        return f"Legal address for {self.user}"

    @property
    def street_address(self):
        """Return the list of street address lines"""
        return [
            line
            for line in [
                self.street_address_1,
                self.street_address_2,
                self.street_address_3,
                self.street_address_4,
                self.street_address_5,
            ]
            if line
        ]

    @property
    def is_complete(self):
        """Returns True if the profile is complete"""
        country = pycountry.countries.get(alpha_2=self.country)
        return all(
            (
                self.first_name,
                self.last_name,
                self.street_address,
                self.city,
                self.country,
                self.state_or_territory
                or country not in COUNTRIES_REQUIRING_POSTAL_CODE,
                self.postal_code or country not in COUNTRIES_REQUIRING_POSTAL_CODE,
            )
        )


class Profile(TimestampedModel):
    """Used to store information about the User"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    name = models.TextField(blank=True)
    fluidreview_id = models.IntegerField(null=True, blank=True)
    smapply_id = models.IntegerField(null=True, blank=True)

    smapply_user_data = models.JSONField(blank=True, null=True)
    smapply_demographic_data = models.JSONField(blank=True, null=True)

    gender = models.CharField(
        max_length=10, blank=True, choices=GENDER_CHOICES, default=""
    )
    birth_year = models.IntegerField(null=True, blank=True)

    company = models.CharField(max_length=128, blank=True, default="")
    job_title = models.CharField(max_length=128, blank=True, default="")
    industry = models.CharField(max_length=60, blank=True, default="")
    job_function = models.CharField(max_length=60, blank=True, default="")
    company_size = models.IntegerField(
        null=True, blank=True, choices=COMPANY_SIZE_CHOICES
    )
    years_experience = models.IntegerField(
        null=True, blank=True, choices=YRS_EXPERIENCE_CHOICES
    )
    highest_education = models.CharField(
        max_length=60, blank=True, default="", choices=HIGHEST_EDUCATION_CHOICES
    )
    can_skip_application_steps = models.BooleanField(default=False)

    @property
    def is_complete(self):
        """Returns True if the profile is complete"""
        return not any(
            map(
                is_blank,
                [
                    self.gender,
                    self.birth_year,
                    self.company,
                    self.job_title,
                    self.industry,
                    self.job_function,
                    self.company_size,
                    self.years_experience,
                    self.highest_education,
                ],
            )
        )

    @property
    def first_name(self):
        """Returns the first name of the profile user"""
        return profile_api.get_first_and_last_names(self.user)[0]

    @property
    def last_name(self):
        """Returns the last name of the profile user"""
        return profile_api.get_first_and_last_names(self.user)[1]

    def __str__(self):
        return "Profile for user {}".format(self.user)
