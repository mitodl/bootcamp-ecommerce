"""Tests for profiles.serializers"""
import pytest

from rest_framework.exceptions import ValidationError

from profiles.factories import UserFactory, LegalAddressFactory
from profiles.models import ChangeEmailRequest
from profiles.serializers import ChangeEmailRequestUpdateSerializer
from profiles.serializers import LegalAddressSerializer, UserSerializer


# pylint:disable=redefined-outer-name


@pytest.fixture()
def mock_user_sync(mocker):
    """ Yield a mock hubspot_sync update task for contacts """
    yield mocker.patch("hubspot_sync.tasks.sync_contact_with_hubspot.delay")


@pytest.fixture()
def sample_address():
    """ Return a legal address"""
    return {
        "first_name": "Test",
        "last_name": "User",
        "street_address_1": "11 Main Street",
        "street_address_2": "Apt # 12",
        "country": "US",
        "state_or_territory": "US-CO",
        "city": "Boulder",
        "postal_code": "80309",
    }


@pytest.mark.django_db
@pytest.mark.parametrize("is_complete", [True, False])
def test_complete_address(is_complete):
    """Test that is_complete in serializer has correct value"""
    address = LegalAddressFactory.create(
        street_address_1=("Main St" if is_complete else "")
    )
    serializer = LegalAddressSerializer(instance=address)
    assert serializer.data["is_complete"] is is_complete


def test_validate_legal_address(sample_address):
    """ Test that correct address data validates"""
    serializer = LegalAddressSerializer(data=sample_address)
    assert serializer.is_valid() is True


@pytest.mark.parametrize(
    "field,value,error",
    [
        ["first_name", "", "This field may not be blank."],
        ["last_name", "", "This field may not be blank."],
        ["street_address", [], "street_address must be a list of street lines"],
        [
            "street_address",
            ["a", "b", "c", "d", "e", "f"],
            "street_address list must be 5 items or less",
        ],
        [
            "street_address",
            ["x" * 61],
            "street_address lines must be 60 characters or less",
        ],
        ["country", "", "This field may not be blank."],
        ["country", None, "This field may not be null."],
        ["state_or_territory", "", "State/territory is required for United States"],
        [
            "state_or_territory",
            "CA-QC",
            "Quebec is not a valid state or territory of United States",
        ],
        ["city", "", "This field may not be blank."],
        ["postal_code", "", "Postal Code is required for United States"],
        [
            "postal_code",
            "3082",
            "Postal Code must be in the format 'NNNNN' or 'NNNNN-NNNNN'",
        ],
    ],
)
def test_validate_required_fields_US_CA(sample_address, field, value, error):
    """ Test that missing required fields causes a validation error"""
    sample_address[field] = value
    serializer = LegalAddressSerializer(data=sample_address)
    assert serializer.is_valid() is False
    assert str(serializer.errors[field][0]) == error


@pytest.mark.parametrize(
    "data,error",
    [
        [
            {"country": "US", "state_or_territory": "US-MA", "postal_code": "2183"},
            "Postal Code must be in the format 'NNNNN' or 'NNNNN-NNNNN'",
        ],
        [
            {"country": "CA", "state_or_territory": "CA-BC", "postal_code": "AFA D"},
            "Postal Code must be in the format 'ANA NAN'",
        ],
    ],
)
def test_validate_postal_code_formats(sample_address, data, error):
    """Test that correct errors are shown for invalid US/CA postal code formats"""
    sample_address.update(data)
    serializer = LegalAddressSerializer(data=sample_address)
    assert serializer.is_valid() is False
    assert str(serializer.errors["postal_code"][0]) == error


@pytest.mark.parametrize("postal_code", ["K0M 2K0", "J8R 3P7", "G3G 2B7", "l6l 1c2"])
def test_valid_ca_postal_codes(sample_address, postal_code):
    """Test that validator won't show error on valid postal code for CA."""

    sample_address.update(
        {"country": "CA", "state_or_territory": "CA-BC", "postal_code": postal_code}
    )

    assert LegalAddressSerializer(data=sample_address).is_valid()


@pytest.mark.parametrize(
    "postal_code", ["0M0 2K0", "J8R P7Q", "GAG 2B7", "L6L 122", "K0M-2K0"]
)
def test_invalid_ca_postal_codes(sample_address, postal_code):
    """Test that validator will show error on invalid postal code for CA."""

    expected_error = "Postal Code must be in the format 'ANA NAN'"
    sample_address.update(
        {"country": "CA", "state_or_territory": "CA-BC", "postal_code": postal_code}
    )

    serializer = LegalAddressSerializer(data=sample_address)
    assert serializer.is_valid() is False
    assert str(serializer.errors["postal_code"][0]) == expected_error


def test_validate_optional_country_data(sample_address):
    """Test that state_or_territory and postal_code are optional for other countries besides US/CA"""
    sample_address.update(
        {"country": "FR", "state_or_territory": "", "postal_code": ""}
    )
    assert LegalAddressSerializer(data=sample_address).is_valid()


@pytest.mark.parametrize("MITOL_HUBSPOT_API_PRIVATE_TOKEN", [None, "fake-key"])
def test_update_user_serializer(
    mock_user_sync, settings, user, sample_address, MITOL_HUBSPOT_API_PRIVATE_TOKEN
):
    """ Test that a UserSerializer can be updated properly and hubspot_sync sync called if appropriate """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = MITOL_HUBSPOT_API_PRIVATE_TOKEN
    serializer = UserSerializer(
        instance=user,
        data={"password": "AgJw0123", "legal_address": sample_address},
        partial=True,
    )
    assert serializer.is_valid()
    serializer.save()
    assert user.legal_address.street_address_1 == sample_address.get("street_address_1")
    if MITOL_HUBSPOT_API_PRIVATE_TOKEN is not None:
        mock_user_sync.assert_called_with(user.id)
    else:
        mock_user_sync.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("MITOL_HUBSPOT_API_PRIVATE_TOKEN", [None, "fake-key"])
def test_create_user_serializer(
    mock_user_sync, settings, sample_address, MITOL_HUBSPOT_API_PRIVATE_TOKEN
):
    """ Test that a UserSerializer can be created properly and hubspot_sync sync called if appropriate """
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = MITOL_HUBSPOT_API_PRIVATE_TOKEN
    serializer = UserSerializer(
        data={
            "username": "fakename",
            "email": "fake@fake.edu",
            "password": "fake",
            "legal_address": sample_address,
        }
    )

    assert serializer.is_valid()
    user = serializer.save()
    assert user.is_active is False
    if MITOL_HUBSPOT_API_PRIVATE_TOKEN is not None:
        mock_user_sync.assert_called_with(user.id)
    else:
        mock_user_sync.assert_not_called()


def test_update_email_change_request_existing_email(user):
    """Test that update change email request gives validation error for existing user email"""
    new_user = UserFactory.create()
    change_request = ChangeEmailRequest.objects.create(
        user=user, new_email=new_user.email
    )
    serializer = ChangeEmailRequestUpdateSerializer(change_request, {"confirmed": True})

    with pytest.raises(ValidationError):
        serializer.is_valid()
        serializer.save()


def test_create_email_change_request_same_email(user):
    """Test that update change email request gives validation error for same user email"""
    change_request = ChangeEmailRequest.objects.create(user=user, new_email=user.email)
    serializer = ChangeEmailRequestUpdateSerializer(change_request, {"confirmed": True})

    with pytest.raises(ValidationError):
        serializer.is_valid()
        serializer.save()


def test_update_user_email(user):
    """Test that updating user email takes the correct action"""
    new_email = "abc@example.com"

    change_request = ChangeEmailRequest.objects.create(user=user, new_email=new_email)
    serializer = ChangeEmailRequestUpdateSerializer(change_request, {"confirmed": True})

    assert serializer.is_valid() is True
    serializer.save()

    user.refresh_from_db()
    assert user.email == new_email


def test_legal_address_serializer_invalid_name(sample_address):
    """ Test that LegalAddressSerializer raises an exception if first/last name is not valid """

    # To make sure that this test isn't flaky, Checking all the character and sequences that should match our name regex

    # Case 1: Make sure that invalid character(s) doesn't exist within the name
    for invalid_character in "~!@&)(+:'.?/,`-":
        # Replace the invalid character on 3 different places within name for rigorous testing of this case
        sample_address["first_name"] = "{0}First{0} Name{0}".format(invalid_character)
        sample_address["last_name"] = "{0}Last{0} Name{0}".format(invalid_character)
        serializer = LegalAddressSerializer(data=sample_address)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    # Case 2: Make sure that name doesn't start with valid special character(s)
    # These characters are valid for a name but they shouldn't be at the start of it
    for valid_character in '^/^$#*=[]`%_;<>{}"|':
        sample_address["first_name"] = "{}First".format(valid_character)
        sample_address["last_name"] = "{}Last".format(valid_character)
        serializer = LegalAddressSerializer(data=sample_address)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
