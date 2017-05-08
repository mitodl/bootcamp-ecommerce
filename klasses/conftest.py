"""
conftest for pytest in this module
"""
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from klasses.models import Bootcamp


def patch_get_admissions(mocker, user):
    """
    Helper function to build admission service responses based on the local database.
    """
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient._get_admissions',
        autospec=True,
        return_value={
            "user": user.email,
            "bootcamps": [
                {
                    "bootcamp_id": None,  # NOTE:this is the ID on the remote web service (we do not need it)
                    "bootcamp_title": bootcamp.title,
                    "klasses": [
                        {
                            "klass_id": klass.klass_key,  # NOTE: this is the ID on the remote web service
                            "klass_name": klass.title,
                            "is_user_eligible_to_pay": True
                        } for klass in bootcamp.klass_set.order_by('id')
                    ]
                } for bootcamp in Bootcamp.objects.all().order_by('id')
            ]
        }
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
