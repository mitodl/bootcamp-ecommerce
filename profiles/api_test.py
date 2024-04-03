"""Tests for user api"""

from pathlib import Path
from datetime import datetime
import logging
import factory
import pytest

from django.contrib.auth import get_user_model

from ecommerce.factories import BootcampRunFactory
from klasses.models import BootcampRun, BootcampRunEnrollment
from profiles.api import (
    get_user_by_id,
    fetch_user,
    fetch_users,
    find_available_username,
    get_first_and_last_names,
    is_user_info_complete,
    parse_alumni_csv,
    Alum,
    import_alum,
    import_alumni,
)
from profiles.exceptions import AlumImportException
from profiles.factories import UserFactory, LegalAddressFactory, ProfileFactory
from profiles.utils import usernameify

User = get_user_model()


def test_get_user_by_id(user):
    """Tests get_user_by_id"""
    assert get_user_by_id(user.id) == user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "prop,value,db_value",
    [
        ["username", "abcdefgh", None],
        ["id", 100, None],
        ["id", "100", 100],
        ["email", "abc@example.com", None],
    ],
)
def test_fetch_user(prop, value, db_value):
    """
    fetch_user should return a User that matches a provided value which represents
    an id, email, or username
    """
    user = UserFactory.create(**{prop: db_value or value})
    found_user = fetch_user(value)
    assert user == found_user


@pytest.mark.django_db
def test_fetch_user_case_sens():
    """fetch_user should be able to fetch a User with a case-insensitive filter"""
    email = "abc@example.com"
    user = UserFactory.create(email=email)
    upper_email = email.upper()
    with pytest.raises(User.DoesNotExist):
        fetch_user(upper_email, ignore_case=False)
    assert fetch_user(upper_email, ignore_case=True) == user


@pytest.mark.django_db
def test_fetch_user_fail():
    """fetch_user should raise an exception if a matching User was not found"""
    with pytest.raises(User.DoesNotExist):
        fetch_user("missingemail@example.com")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "prop,values,db_values",
    [
        ["username", ["abcdefgh", "ijklmnop", "qrstuvwxyz"], None],
        ["id", [100, 101, 102], None],
        ["id", ["100", "101", "102"], [100, 101, 102]],
        ["email", ["abc@example.com", "def@example.com", "ghi@example.com"], None],
    ],
)
def test_fetch_users(prop, values, db_values):
    """
    fetch_users should return a set of Users that match some provided values which represent
    ids, emails, or usernames
    """
    users = UserFactory.create_batch(
        len(values), **{prop: factory.Iterator(db_values or values)}
    )
    found_users = fetch_users(values)
    assert set(users) == set(found_users)


@pytest.mark.django_db
def test_fetch_users_case_sens():
    """fetch_users should be able to fetch Users with a case-insensitive filter"""
    emails = ["abc@example.com", "def@example.com", "ghi@example.com"]
    users = UserFactory.create_batch(len(emails), email=factory.Iterator(emails))
    upper_emails = list(map(str.upper, emails))
    with pytest.raises(User.DoesNotExist):
        fetch_users(upper_emails, ignore_case=False)
    assert set(fetch_users(upper_emails, ignore_case=True)) == set(users)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "prop,existing_values,missing_values",
    [
        ["username", ["abcdefgh"], ["ijklmnop", "qrstuvwxyz"]],
        ["id", [100], [101, 102]],
        ["email", ["abc@example.com"], ["def@example.com", "ghi@example.com"]],
    ],
)
def test_fetch_users_fail(prop, existing_values, missing_values):
    """
    fetch_users should raise an exception if any provided values did not match a User, and
    the exception message should contain info about the values that did not match.
    """
    fetch_users_values = existing_values + missing_values
    UserFactory.create_batch(
        len(existing_values), **{prop: factory.Iterator(existing_values)}
    )
    expected_missing_value_output = str(sorted(list(missing_values)))
    with pytest.raises(User.DoesNotExist, match=expected_missing_value_output):
        fetch_users(fetch_users_values)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "username_base,suffixed_to_create,expected_available_username",
    [
        ["someuser", 0, "someuser1"],
        ["someuser", 5, "someuser6"],
        ["abcdefghij", 10, "abcdefgh11"],
        ["abcdefghi", 99, "abcdefg100"],
    ],
)
def test_find_available_username(
    mocker, username_base, suffixed_to_create, expected_available_username
):
    """find_available_username should return an available username with the lowest possible suffix"""
    # Change the username max length to 10 for test data simplicity's sake
    temp_username_max_len = 10
    mocker.patch("profiles.api.USERNAME_MAX_LEN", temp_username_max_len)

    def suffixed_username_generator():
        """Generator for usernames with suffixes that will not exceed the username character limit"""
        for suffix_int in range(1, suffixed_to_create + 1):
            suffix = str(suffix_int)
            username = "{}{}".format(username_base, suffix)
            if len(username) <= temp_username_max_len:
                yield username
            else:
                num_extra_characters = len(username) - temp_username_max_len
                yield "{}{}".format(
                    username_base[0 : len(username_base) - num_extra_characters], suffix
                )

    UserFactory.create(username=username_base)
    UserFactory.create_batch(
        suffixed_to_create, username=factory.Iterator(suffixed_username_generator())
    )
    available_username = find_available_username(username_base)
    assert available_username == expected_available_username


@pytest.mark.django_db
def test_full_username_creation():
    """
    Integration test to ensure that the USERNAME_MAX_LEN constant is set correctly, and that
    generated usernames do not exceed it.
    """
    expected_username_max = 30
    user_full_name = "Longerton McLongernamenbergenstein"
    generated_username = usernameify(user_full_name)
    assert len(generated_username) == expected_username_max
    UserFactory.create(username=generated_username, profile__name=user_full_name)
    new_user_full_name = "{} Jr.".format(user_full_name)
    new_generated_username = usernameify(new_user_full_name)
    assert new_generated_username == generated_username
    available_username = find_available_username(new_generated_username)
    assert available_username == "{}1".format(
        new_generated_username[0 : expected_username_max - 1]
    )


@pytest.mark.django_db
def test_get_first_and_last_names():
    """get_first_and_last_names should fetch the most reliable values for a user's first and last name"""
    user = UserFactory.create(profile=None, legal_address=None)
    assert get_first_and_last_names(user) == (None, None)
    profile = ProfileFactory.create(user=user, name="Mononymous")
    user.refresh_from_db()
    assert get_first_and_last_names(user) == ("Mononymous", "")
    profile.name = "John Profile"
    profile.save()
    user.refresh_from_db()
    assert get_first_and_last_names(user) == ("John", "Profile")
    LegalAddressFactory.create(user=user, first_name="Jane", last_name="Address")
    user.refresh_from_db()
    assert get_first_and_last_names(user) == ("Jane", "Address")


@pytest.mark.django_db
def test_is_user_info_complete():
    """is_user_info_complete should return True if the user has a fully filled out profile and legal address"""
    user = UserFactory.create(profile=None, legal_address=None)
    assert is_user_info_complete(user) is False
    ProfileFactory.create(user=user)
    LegalAddressFactory.create(user=user)
    assert is_user_info_complete(user) is True


def test_parse_import_alumni_csv():
    """parse_import_alumni_csv should convert CSV input to Alum objects"""
    csv_path = Path(__file__).parent / "testdata" / "example_alumni.csv"
    alumni = parse_alumni_csv(csv_path)
    assert alumni == [
        Alum(
            learner_email="hdoof@odl.mit.edu",
            bootcamp_name="How to be Good",
            bootcamp_run_title="How to be Good Run 1",
            bootcamp_start_date="2018-07-28",
            bootcamp_end_date="2018-12-28",
        ),
        Alum(
            learner_email="example@odl.mit.edu",
            bootcamp_name="How to be Good",
            bootcamp_run_title="How to be Good Run 2",
            bootcamp_start_date="2018-08-28",
            bootcamp_end_date="2018-12-28",
        ),
    ]


def test_parse_alumni_csv_no_header(tmp_path):
    """parse_alumni_csv should error if no header is found"""
    path = tmp_path / "test.csv"
    open(path, "w")  # create file
    with pytest.raises(AlumImportException) as ex:
        parse_alumni_csv(path)

    assert ex.value.args[0] == "Unable to find the header row"


def test_parse_alumni_csv_missing_header(tmp_path):
    """parse_alumni_csv should error if not all fields are present"""
    path = tmp_path / "test.csv"
    with open(path, "w") as f:
        f.write("Learner Email\n")
        f.write("hdoof@odl.mit.edu\n")

    with pytest.raises(AlumImportException) as ex:
        parse_alumni_csv(path)

    assert ex.value.args[0] == "Unable to find column header Bootcamp Name"


@pytest.mark.django_db
def test_import_alumni_missing_bootcamp():
    """test the failure becuase of missing bootcamp"""
    alum = Alum(
        learner_email="hdoof@odl.mit.edu",
        bootcamp_name="How to be Evil",
        bootcamp_run_title="How to be Evil Run 1",
        bootcamp_start_date="2018-07-28",
        bootcamp_end_date="2018-12-28",
    )
    with pytest.raises(BootcampRun.DoesNotExist):
        import_alum(alum)


@pytest.mark.django_db
def test_import_alumni_with_enrollment(caplog):
    """check the enrollment created for the user"""
    caplog.set_level(logging.INFO)
    run = BootcampRunFactory.create(
        title="How to be Evil Run 1",
        bootcamp__title="How to be Evil",
        start_date=datetime(2019, 9, 21),
        end_date=datetime(2019, 12, 21),
    )
    alum = Alum(
        learner_email="hdoof@odl.mit.edu",
        bootcamp_name="How to be Evil",
        bootcamp_run_title="How to be Evil Run 1",
        bootcamp_start_date="2019-09-21",
        bootcamp_end_date="2019-12-21",
    )

    with pytest.raises(User.DoesNotExist):
        User.objects.get(email="hdoof@odl.mit.edu")
    with pytest.raises(BootcampRunEnrollment.DoesNotExist):
        BootcampRunEnrollment.objects.get(
            user__email="hdoof@odl.mit.edu", bootcamp_run=run
        )

    import_alum(alum)
    assert (
        "User does not exist against that email=hdoof@odl.mit.edu but created without password and incomplete profile"
        in caplog.text
    )
    assert (
        "User=hdoof@odl.mit.edu successfully enrolled in bootcamp run How to be Evil Run 1"
        in caplog.text
    )

    user = User.objects.get(email="hdoof@odl.mit.edu")
    assert user
    assert user.username == "hdoof"
    enrollment = BootcampRunEnrollment.objects.get(
        user__email="hdoof@odl.mit.edu", bootcamp_run=run
    )
    assert enrollment
    assert enrollment.user == user
    assert enrollment.bootcamp_run == run
    assert enrollment.user.profile.can_skip_application_steps
    assert enrollment.user_certificate_is_blocked is False

    # check for alreading existing enrollments
    import_alum(alum)
    assert (
        "User=hdoof@odl.mit.edu already exists in bootcamp run How to be Evil Run 1"
        in caplog.text
    )


@pytest.mark.django_db
def test_import_alumni(mocker):
    """import_alumni should iterate through the list of alum, processing one at a time"""
    import_mock = mocker.patch("profiles.api.import_alum")
    csv_path = Path(__file__).parent / "testdata" / "example_alumni.csv"
    import_alumni(csv_path)
    alumni = parse_alumni_csv(csv_path)
    for alum in alumni:
        import_mock.assert_any_call(alum)


@pytest.mark.django_db
def test_import_alumni_error(mocker):
    """import_alumni should reraise errors"""
    mocker.patch("profiles.api.import_alum", side_effect=ZeroDivisionError)
    csv_path = Path(__file__).parent / "testdata" / "example_alumni.csv"
    with pytest.raises(AlumImportException):
        import_alumni(csv_path)
