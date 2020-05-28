"""
conftest for pytest in this module
"""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture()
def mocked_requests_get(mocker):
    """
    Generic mock for requests.get
    """
    mocked_get_func = mocker.patch("requests.get", autospec=True)
    mocked_response = Mock()
    mocked_get_func.return_value = mocked_response
    return SimpleNamespace(request=mocked_get_func, response=mocked_response)
