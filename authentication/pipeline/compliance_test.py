"""Compliance pipeline tests"""
import pytest
from social_core.exceptions import AuthException

from authentication.exceptions import (
    UserExportBlockedException,
    UserTryAgainLaterException,
)
from authentication.pipeline import compliance
from compliance.factories import ExportsInquiryLogFactory


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def social_auth_settings(settings):
    """ Enable social auth API by default """
    settings.FEATURES["SOCIAL_AUTH_API"] = True


def test_verify_exports_compliance_disabled(mocker, mock_create_user_strategy):
    """Assert that nothing is done when the api is disabled"""
    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.is_exports_verification_enabled.return_value = False

    assert compliance.verify_exports_compliance(mock_create_user_strategy, None) == {}
    mock_api.is_exports_verification_enabled.assert_called_once()


def test_verify_api_disabled_no_compliance_check(mocker, mock_create_user_strategy):
    """Assert that nothing is done when the social auth api is disabled"""
    mock_create_user_strategy.is_api_enabled.return_value = False
    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.is_exports_verification_enabled.return_value = False

    assert compliance.verify_exports_compliance(mock_create_user_strategy, None) == {}
    mock_api.is_exports_verification_enabled.assert_not_called()


@pytest.mark.parametrize(
    "is_active, inquiry_exists, should_verify",
    [
        [True, True, False],
        [True, False, True],
        [False, True, True],
        [False, False, True],
    ],
)
def test_verify_exports_compliance_user_active(
    mailoutbox,
    mocker,
    mock_create_user_strategy,
    user,
    is_active,
    inquiry_exists,
    should_verify,
):  # pylint: disable=too-many-arguments
    """Assert that the user is verified only if they already haven't been"""
    user.is_active = is_active
    if inquiry_exists:
        ExportsInquiryLogFactory.create(user=user)

    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.verify_user_with_exports.return_value = mocker.Mock(
        is_denied=False, is_unknown=False
    )

    assert (
        compliance.verify_exports_compliance(mock_create_user_strategy, None, user=user)
        == {}
    )

    if should_verify:
        mock_api.verify_user_with_exports.assert_called_once_with(user)
    assert len(mailoutbox) == 0


def test_verify_exports_compliance_no_record(mocker, mock_create_user_strategy, user):
    """Assert that an error to try again later is raised if no ExportsInquiryLog is created"""

    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.verify_user_with_exports.return_value = None

    with pytest.raises(UserTryAgainLaterException):
        compliance.verify_exports_compliance(mock_create_user_strategy, None, user=user)

    mock_api.verify_user_with_exports.assert_called_once_with(user)


def test_verify_exports_compliance_api_raises_exception(
    mocker, mock_create_user_strategy, user
):
    """Assert that an error to try again later is raised if the export api raises an exception"""

    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.verify_user_with_exports.side_effect = Exception("error")

    with pytest.raises(UserTryAgainLaterException):
        compliance.verify_exports_compliance(mock_create_user_strategy, None, user=user)

    mock_api.verify_user_with_exports.assert_called_once_with(user)


@pytest.mark.parametrize("email_fails", [True, False])
def test_verify_exports_compliance_denied(
    mailoutbox, mocker, mock_create_user_strategy, user, email_fails
):
    """Assert that a UserExportBlockedException is raised if the inquiry result is denied"""
    reason_code = 100
    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.verify_user_with_exports.return_value = mocker.Mock(
        is_denied=True, is_unknown=False, reason_code=reason_code, info_code="123"
    )

    if email_fails:
        # a mail sending error should not obscure the true error
        mocker.patch(
            "authentication.pipeline.compliance.mail.send_mail",
            side_effect=Exception("mail error"),
        )

    with pytest.raises(UserExportBlockedException) as exc:
        compliance.verify_exports_compliance(mock_create_user_strategy, None, user=user)

    assert exc.value.reason_code == reason_code

    mock_api.verify_user_with_exports.assert_called_once_with(user)
    assert len(mailoutbox) == (0 if email_fails else 1)


def test_verify_exports_compliance_unknown(
    mailoutbox, mocker, mock_create_user_strategy, user
):
    """Assert that a UserExportBlockedException is raised if the inquiry result is unknown"""
    mock_api = mocker.patch("authentication.pipeline.compliance.api")
    mock_api.verify_user_with_exports.return_value = mocker.Mock(
        is_denied=False, is_unknown=True
    )

    with pytest.raises(AuthException):
        compliance.verify_exports_compliance(mock_create_user_strategy, None, user=user)

    mock_api.verify_user_with_exports.assert_called_once_with(user)
    assert len(mailoutbox) == 0
