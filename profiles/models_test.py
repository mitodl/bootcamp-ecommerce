"""
Tests for profiles.models
"""
from builtins import setattr

import pytest

from profiles.factories import LegalAddressFactory, ProfileFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    "empty_field",
    [
        "first_name",
        "last_name",
        "street_address_1",
        "city",
        "country",
        "state_or_territory",
        None,
    ],
)
def test_legal_address_is_complete(empty_field):
    """Test that LegalAddress.is_complete returns expected result"""
    address = LegalAddressFactory.create(country="US")
    if empty_field:
        setattr(address, empty_field, "")
        assert address.is_complete is False
    else:
        assert address.is_complete is True


@pytest.mark.parametrize(
    "empty_field",
    [
        "birth_year",
        "gender",
        "job_title",
        "company",
        "industry",
        "job_function",
        "company_size",
        "years_experience",
        "highest_education",
        None,
    ],
)
def test_profile_is_complete(empty_field):
    """Test that Profile.is_complete returns expected result"""
    profile = ProfileFactory.create()
    if empty_field:
        setattr(profile, empty_field, "")
        assert profile.is_complete is False
    else:
        assert profile.is_complete is True
