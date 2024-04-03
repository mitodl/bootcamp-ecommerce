"""User utils tests"""

import pytest
from profiles.utils import ensure_active_user, is_duplicate_username_error, usernameify


@pytest.mark.parametrize(
    "full_name,email,expected_username",
    [
        [" John  Doe ", None, "john-doe"],
        ["Tabby	Tabberson", None, "tabby-tabberson"],
        ["Àccèntèd Ñame, Ësq.", None, "àccèntèd-ñame-ësq"],
        ["-Dashy_St._Underscores-", None, "dashy-st-underscores"],
        ["Repeated-----Chars___Jr.", None, "repeated-chars-jr"],
        ["Numbers123 !$!@ McStrange!!##^", None, "numbers-mcstrange"],
        ["Кирил Френков", None, "кирил-френков"],
        ["年號", None, "年號"],
        ["abcdefghijklmnopqrstuvwxyz", None, "abcdefghijklmnopqrst"],
        ["ai bi cı dI eİ fI", None, "ai-bi-ci-di-ei-fi"],
        ["", "some.email@example.co.uk", "someemail"],
    ],
)
def test_usernameify(mocker, full_name, email, expected_username):
    """usernameify should turn a user's name into a username, or use the email if necessary"""
    # Change the username max length to 20 for test data simplicity's sake
    temp_username_max_len = 20
    mocker.patch("profiles.utils.USERNAME_MAX_LEN", temp_username_max_len)
    patched_log_error = mocker.patch("profiles.utils.log.error")

    assert usernameify(full_name, email=email) == expected_username
    assert patched_log_error.called == bool(email and not full_name)


def test_usernameify_fail():
    """usernameify should raise an exception if the full name and email both fail to produce a username"""
    with pytest.raises(ValueError):
        assert usernameify("!!!", email="???@example.com")


@pytest.mark.parametrize(
    "exception_text,expected_value",
    [
        ["DETAILS: (username)=(ABCDEFG) already exists", True],
        ["DETAILS: (email)=(ABCDEFG) already exists", False],
    ],
)
def test_is_duplicate_username_error(exception_text, expected_value):
    """
    is_duplicate_username_error should return True if the exception text provided indicates a duplicate username error
    """
    assert is_duplicate_username_error(exception_text) is expected_value


def test_ensure_active_user(user):
    """
    Test that ensure_active_user activates
    """
    user.is_active = False
    user.save()

    assert not user.is_active

    ensure_active_user(user)
    assert user.is_active
