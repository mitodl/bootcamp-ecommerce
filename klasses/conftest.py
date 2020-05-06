"""
conftest for pytest in this module
"""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from klasses.models import BootcampRun


def patch_get_admissions(mocker):
    """
    Helper function to build admission service responses based on the local database.
    """
    mocker.patch(
        'klasses.bootcamp_admissions_client.fetch_smapply_run_keys',
        autospec=True,
        return_value=list(BootcampRun.objects.all().values_list('run_key', flat=True))
    )


@pytest.fixture()
def mocked_requests_get(mocker):
    """
    Generic mock for requests.get
    """
    mocked_get_func = mocker.patch('requests.get', autospec=True)
    mocked_response = Mock()
    mocked_get_func.return_value = mocked_response
    return SimpleNamespace(
        request=mocked_get_func,
        response=mocked_response
    )
