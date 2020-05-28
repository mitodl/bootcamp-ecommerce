"""
Fixtures for pipeline tests
"""
import pytest


@pytest.fixture
def mock_create_user_strategy(mocker):
    """Fixture that returns a valid strategy for create_user_via_email"""
    strategy = mocker.Mock()
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
