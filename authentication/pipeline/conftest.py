"""
Fixtures for pipeline tests
"""
import pytest


@pytest.fixture
def backend_settings(settings):
    """A dictionary of settings for the backend"""
    return {"USER_FIELDS": settings.SOCIAL_AUTH_EMAIL_USER_FIELDS}


@pytest.fixture
def mock_email_backend(mocker, backend_settings):  # pylint:disable=redefined-outer-name
    """Fixture that returns a fake EmailAuth backend object"""
    backend = mocker.Mock()
    backend.name = "email"
    backend.setting.side_effect = lambda key, default, **kwargs: backend_settings.get(
        key, default
    )
    return backend


@pytest.fixture
def mock_create_user_strategy(mocker):
    """Fixture that returns a valid strategy for create_user_via_email"""
    strategy = mocker.Mock(request=mocker.Mock(session={}))
    strategy.request_data.return_value = {
        "profile": {"name": "Jane Doe"},
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
    strategy.is_api_enabled = mocker.Mock(return_value=True)
    return strategy
