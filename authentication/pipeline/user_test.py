"""Tests of user pipeline actions"""
# pylint: disable=redefined-outer-name

from django.contrib.sessions.middleware import SessionMiddleware
import pytest
from social_django.utils import load_strategy, load_backend

from profiles.factories import UserFactory
from authentication.pipeline import user as user_actions
from authentication.exceptions import (
    InvalidPasswordException,
    RequirePasswordException,
    RequireRegistrationException,
    RequirePasswordAndPersonalInfoException,
    RequireProfileException,
    UserCreationFailedException,
)
from authentication.utils import SocialAuthState
from compliance.constants import RESULT_SUCCESS, RESULT_DENIED, RESULT_UNKNOWN
from compliance.factories import ExportsInquiryLogFactory


@pytest.fixture
def mock_create_profile_strategy(mocker):
    """Fixture that returns a valid strategy for create_profile"""
    strategy = mocker.Mock()
    strategy.request_data.return_value = {
        "gender": "f",
        "birth_year": "2000",
        "company": "MIT",
        "job_title": "QA Tester",
    }
    return strategy


def validate_email_auth_request_not_email_backend(mocker):
    """Tests that validate_email_auth_request return if not using the email backend"""
    mock_strategy = mocker.Mock()
    mock_backend = mocker.Mock()
    mock_backend.name = "notemail"
    assert user_actions.validate_email_auth_request(mock_strategy, mock_backend) == {}


@pytest.mark.parametrize(
    "has_user,expected", [(True, {"flow": SocialAuthState.FLOW_LOGIN}), (False, {})]
)
@pytest.mark.django_db
def test_validate_email_auth_request(rf, has_user, expected):
    """Test that validate_email_auth_request returns correctly given the input"""
    request = rf.post("/complete/email")
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)

    user = UserFactory.create() if has_user else None

    assert (
        user_actions.validate_email_auth_request(
            strategy, backend, pipeline_index=0, user=user
        )
        == expected
    )


def test_get_username(mocker, user):
    """Tests that we get a username for a new user"""
    mock_strategy = mocker.Mock()
    mock_strategy.storage.user.get_username.return_value = user.username
    assert user_actions.get_username(mock_strategy, None, user) == {
        "username": user.username
    }
    mock_strategy.storage.user.get_username.assert_called_once_with(user)


def test_get_username_no_user(mocker):
    """Tests that get_username returns None if there is no User"""
    mock_strategy = mocker.Mock()
    assert user_actions.get_username(mock_strategy, None, None)["username"] is None
    mock_strategy.storage.user.get_username.assert_not_called()


def test_user_password_not_email_backend(mocker):
    """Tests that user_password return if not using the email backend"""
    mock_strategy = mocker.MagicMock()
    mock_user = mocker.Mock()
    mock_backend = mocker.Mock()
    mock_backend.name = "notemail"
    assert (
        user_actions.validate_password(
            mock_strategy,
            mock_backend,
            pipeline_index=0,
            user=mock_user,
            flow=SocialAuthState.FLOW_LOGIN,
        )
        == {}
    )
    # make sure we didn't update or check the password
    mock_user.set_password.assert_not_called()
    mock_user.save.assert_not_called()
    mock_user.check_password.assert_not_called()


@pytest.mark.parametrize("user_password", ["abc123", "def456"])
def test_user_password_login(rf, user, user_password):
    """Tests that user_password works for login case"""
    request_password = "abc123"
    user.set_password(user_password)
    user.save()
    request = rf.post(
        "/complete/email", {"password": request_password, "email": user.email}
    )
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)

    if request_password == user_password:
        assert (
            user_actions.validate_password(
                strategy,
                backend,
                pipeline_index=0,
                user=user,
                flow=SocialAuthState.FLOW_LOGIN,
            )
            == {}
        )
    else:
        with pytest.raises(InvalidPasswordException):
            user_actions.validate_password(
                strategy,
                backend,
                pipeline_index=0,
                user=user,
                flow=SocialAuthState.FLOW_LOGIN,
            )


def test_user_password_not_login(rf, user):
    """
    Tests that user_password performs denies authentication
    for an existing user if password not provided regardless of auth_type
    """
    user.set_password("abc123")
    user.save()
    request = rf.post("/complete/email", {"email": user.email})
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)

    with pytest.raises(RequirePasswordException):
        user_actions.validate_password(
            strategy,
            backend,
            pipeline_index=0,
            user=user,
            flow=SocialAuthState.FLOW_LOGIN,
        )


def test_user_password_not_exists(rf):
    """Tests that user_password raises auth error for nonexistent user"""
    request = rf.post(
        "/complete/email", {"password": "abc123", "email": "doesntexist@localhost"}
    )
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)

    with pytest.raises(RequireRegistrationException):
        user_actions.validate_password(
            strategy,
            backend,
            pipeline_index=0,
            user=None,
            flow=SocialAuthState.FLOW_LOGIN,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "has_user,is_api_enabled,incomplete_address",
    [
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, False, True),
    ],
)
def test_create_user_via_email_exit(
    mocker, has_user, is_api_enabled, incomplete_address
):
    """
    Tests that create_user_via_email returns if the user exists or the api is disabled
    """
    user = UserFactory.create(legal_address__incomplete=incomplete_address)
    user.set_password("123")
    mock_strategy = mocker.Mock()
    mock_strategy.is_api_enabled.return_value = is_api_enabled
    mock_backend = mocker.Mock()
    assert (
        user_actions.create_user_via_email(
            mock_strategy,
            mock_backend,
            pipeline_index=0,
            user=user if has_user else None,
        )
        == {}
    )

    mock_strategy.request_data.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("is_new", [True, False])
def test_create_user_via_email(
    mocker, mock_email_backend, mock_create_user_strategy, is_new
):
    """
    Tests that create_user_via_email creates a user via social_core.pipeline.user.create_user_via_email,
    generates a username, and sets a name and password
    """
    user = UserFactory.create(legal_address__incomplete=True)
    patched_usernameify = mocker.patch(
        "authentication.pipeline.user.usernameify", return_value=user.username
    )
    patched_create_user = mocker.patch(
        "authentication.pipeline.user.create_user_with_generated_username",
        return_value=user,
    )

    response = user_actions.create_user_via_email(
        mock_create_user_strategy,
        mock_email_backend,
        details=dict(email=user.email),
        pipeline_index=0,
        flow=SocialAuthState.FLOW_REGISTER,
        user=(None if is_new else user),
    )
    assert response == {"user": user, "username": user.username, "is_new": is_new}
    request_data = mock_create_user_strategy.request_data()
    if is_new:
        patched_usernameify.assert_called_once_with(
            request_data["profile"]["name"], email=user.email
        )
        patched_create_user.assert_called_once()
        # Confirm that a UserSerializer object was passed to create_user_with_generated_username, and
        # that it was instantiated with the data we expect.
        serializer = patched_create_user.call_args_list[0][0][0]
        assert serializer.initial_data["username"] == user.username
        assert serializer.initial_data["email"] == user.email
        assert (
            serializer.initial_data["profile"]["name"]
            == request_data["profile"]["name"]
        )
        assert serializer.initial_data["password"] == request_data["password"]
    else:
        patched_create_user.assert_not_called()
        patched_usernameify.assert_not_called()


@pytest.mark.django_db
def test_create_user_via_email_no_data(mocker, mock_email_backend):
    """Tests that create_user_via_email raises an error if no data for name and password provided"""
    mock_strategy = mocker.Mock()
    mock_strategy.request_data.return_value = {}
    with pytest.raises(RequirePasswordAndPersonalInfoException):
        user_actions.create_user_via_email(
            mock_strategy,
            mock_email_backend,
            pipeline_index=0,
            flow=SocialAuthState.FLOW_REGISTER,
        )


@pytest.mark.django_db
def test_create_user_via_email_with_shorter_name(mocker, mock_email_backend):
    """Tests that create_user_via_email raises an error if name field is shorter than 2 characters"""
    mock_strategy = mocker.Mock()
    mock_strategy.request_data.return_value = {
        "profile": {"name": "a"},
        "password": "password1",
        "legal_address": {
            "first_name": "Jane",
            "last_name": "Doe",
            "street_address_1": "1 Main st",
            "city": "Boston",
            "state_or_territory": "US-MA",
            "country": "US",
            "postal_code": "02101",
        },
    }

    with pytest.raises(RequirePasswordAndPersonalInfoException) as exc:
        user_actions.create_user_via_email(
            mock_strategy,
            mock_email_backend,
            details=dict(email="test@example.com"),
            pipeline_index=0,
            flow=SocialAuthState.FLOW_REGISTER,
        )

    assert exc.value.errors == ["Full name must be at least 2 characters long."]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "create_user_return_val,create_user_exception",
    [[None, None], [UserFactory.build(), ValueError("bad value")]],
)
def test_create_user_via_email_create_fail(
    mocker,
    mock_email_backend,
    mock_create_user_strategy,
    create_user_return_val,
    create_user_exception,
):
    """Tests that create_user_via_email raises an error if user creation fails"""
    patched_create_user = mocker.patch(
        "authentication.pipeline.user.create_user_with_generated_username",
        return_value=create_user_return_val,
        side_effect=create_user_exception,
    )
    with pytest.raises(UserCreationFailedException):
        user_actions.create_user_via_email(
            mock_create_user_strategy,
            mock_email_backend,
            details=dict(email="someuser@example.com"),
            pipeline_index=0,
            flow=SocialAuthState.FLOW_REGISTER,
        )
    patched_create_user.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize("hubspot_key", [None, "fake-key"])
def test_create_profile(
    mock_email_backend, mock_create_profile_strategy, hubspot_key, settings, mocker
):  # pylint:disable=too-many-arguments
    """
    Tests that create_profile creates a profile
    """
    user = UserFactory.create(profile__incomplete=True)
    settings.MITOL_HUBSPOT_API_PRIVATE_TOKEN = hubspot_key
    mock_user_sync = mocker.patch("hubspot_sync.tasks.sync_contact_with_hubspot.delay")
    response = user_actions.create_profile(
        mock_create_profile_strategy,
        mock_email_backend,
        user=user,
        pipeline_index=0,
        flow=SocialAuthState.FLOW_REGISTER,
    )
    assert response == {}
    assert user.profile.gender == mock_create_profile_strategy.request_data().get(
        "gender"
    )
    assert user.profile.company == mock_create_profile_strategy.request_data().get(
        "company"
    )
    if hubspot_key is not None:
        mock_user_sync.assert_called_with(user.id)
    else:
        mock_user_sync.assert_not_called()


@pytest.mark.django_db
def test_create_profile_no_data(mocker, mock_email_backend):
    """Tests that create_profile raises an error if no data for name and password provided"""
    user = UserFactory.create(profile__incomplete=True)
    mock_strategy = mocker.Mock()
    mock_strategy.request_data.return_value = {}
    with pytest.raises(RequireProfileException):
        user_actions.create_profile(
            mock_strategy,
            mock_email_backend,
            user=user,
            pipeline_index=0,
            flow=SocialAuthState.FLOW_REGISTER,
        )


@pytest.mark.parametrize("hijacked", [True, False])
def test_forbid_hijack(mocker, hijacked):
    """
    Tests that forbid_hijack action raises an exception if a user is hijacked
    """
    mock_strategy = mocker.Mock()
    mock_strategy.session_get.return_value = hijacked

    mock_backend = mocker.Mock(name="email")

    args = [mock_strategy, mock_backend]
    kwargs = {"flow": SocialAuthState.FLOW_LOGIN}

    if hijacked:
        with pytest.raises(ValueError):
            user_actions.forbid_hijack(*args, **kwargs)
    else:
        assert user_actions.forbid_hijack(*args, **kwargs) == {}


def test_send_user_to_hubspot(mocker, settings):
    """
    Tests that send_user_to_hubspot sends the correct data
    """
    mock_requests = mocker.patch("authentication.pipeline.user.requests")
    mock_log = mocker.patch("authentication.pipeline.user.log")

    mock_request = mocker.Mock(COOKIES={"hubspotutk": "somefakedata"})

    # Test with no settings set
    ret_val = user_actions.send_user_to_hubspot(
        mock_request, details={"email": "test@test.co"}
    )
    assert ret_val == {}
    mock_log.error.assert_called_once()

    # Test with appropriate settings set
    settings.HUBSPOT_CONFIG["HUBSPOT_PORTAL_ID"] = "123456"
    settings.HUBSPOT_CONFIG["HUBSPOT_CREATE_USER_FORM_ID"] = "abcdefg"
    ret_val = user_actions.send_user_to_hubspot(
        mock_request, details={"email": "test@test.co"}
    )
    assert ret_val == {}

    mock_requests.post.assert_called_with(
        data={"email": "test@test.co", "hs_context": '{"hutk": "somefakedata"}'},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        url="https://forms.hubspot.com/uploads/form/v2/123456/abcdefg?&",
    )


@pytest.mark.parametrize("is_active", [True, False])
@pytest.mark.parametrize("is_new", [True, False])
@pytest.mark.parametrize(
    "is_enabled, has_inquiry, computed_result, expected",
    [
        [True, True, RESULT_SUCCESS, True],  # feature enabled, result is success
        [True, True, RESULT_DENIED, False],  # feature enabled, result is denied
        [True, True, RESULT_UNKNOWN, False],  # feature enabled, result is unknown
        [False, False, None, True],  # feature disabled
        [True, False, None, False],  # feature enabled, no result
    ],
)
def test_activate_user(
    settings,
    mocker,
    mock_create_user_strategy,
    user,
    is_active,
    is_new,
    is_enabled,
    has_inquiry,
    computed_result,
    expected,
):  # pylint: disable=too-many-arguments
    """Test that activate_user takes the correct action"""
    settings.FEATURES["SOCIAL_AUTH_API"] = True
    user.is_active = is_active
    if has_inquiry:
        ExportsInquiryLogFactory.create(user=user, computed_result=computed_result)

    mock_compliance_api = mocker.patch(
        "authentication.pipeline.user.compliance_api.is_exports_verification_enabled",
        return_value=is_enabled,
    )

    assert (
        user_actions.activate_user(
            mock_create_user_strategy, None, user=user, is_new=is_new
        )
        == {}
    )

    if not is_active:
        # only if the user is inactive and just registered
        assert user.is_active is expected
        mock_compliance_api.assert_called_once()
    else:
        mock_compliance_api.assert_not_called()


def test_activate_user_social_auth_disabled(mocker, user, mock_create_user_strategy):
    """Test that activate_user returns {} without checking compliance if social_auth is disabled"""
    mock_compliance_api = mocker.patch(
        "authentication.pipeline.user.compliance_api.is_exports_verification_enabled"
    )
    mock_create_user_strategy.is_api_enabled = mocker.Mock(return_value=False)
    user.is_active = False
    assert (
        user_actions.activate_user(
            mock_create_user_strategy, None, user=user, is_new=False
        )
        == {}
    )
    mock_compliance_api.assert_not_called()
