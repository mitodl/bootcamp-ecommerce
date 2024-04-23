# pylint: disable=redefined-outer-name
"""Test for NovoEd API functionality"""

import pytest

from rest_framework import status
from requests.exceptions import HTTPError
from mitol.common.utils import now_in_utc

from klasses.factories import BootcampRunEnrollmentFactory
from profiles.factories import UserFactory
from novoed.api import enroll_in_novoed_course, unenroll_from_novoed_course
from novoed.constants import REGISTER_USER_URL_STUB, UNENROLL_USER_URL_STUB
from main.test_utils import MockResponse


FAKE_API_KEY = "apikey"
FAKE_API_SECRET = "apisecret"
FAKE_BASE_URL = "http://localhost"
FAKE_COURSE_STUB = "my-course"


@pytest.fixture(autouse=True)
def novoed_settings(settings):
    """NovoEd-related settings values"""
    settings.NOVOED_API_KEY = FAKE_API_KEY
    settings.NOVOED_API_SECRET = FAKE_API_SECRET
    settings.NOVOED_API_BASE_URL = FAKE_BASE_URL


@pytest.fixture
def novoed_user():
    """User to use in NovoEd test cases"""
    return UserFactory.create(
        legal_address__first_name="Jane", legal_address__last_name="Doe"
    )


@pytest.fixture
def patched_post(mocker):
    """Patches the post function from the requests library"""
    return mocker.patch("novoed.api.requests.post")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "response_status,exp_created,exp_existing,exp_update_sync_date",
    [
        [status.HTTP_200_OK, True, False, True],
        [status.HTTP_207_MULTI_STATUS, False, True, True],
        [status.HTTP_204_NO_CONTENT, False, False, False],
    ],
)
def test_enroll_in_novoed_course(
    patched_post,
    novoed_user,
    response_status,
    exp_created,
    exp_existing,
    exp_update_sync_date,
):  # pylint:disable=too-many-arguments
    """
    enroll_in_novoed_course should make a request to enroll a user in NovoEd and return flags indicating the results
    """
    enrollment = BootcampRunEnrollmentFactory.create(
        user=novoed_user,
        bootcamp_run__novoed_course_stub=FAKE_COURSE_STUB,
        novoed_sync_date=None,
    )
    patched_post.return_value = MockResponse(content=None, status_code=response_status)
    result = enroll_in_novoed_course(novoed_user, FAKE_COURSE_STUB)
    patched_post.assert_called_once_with(
        f"{FAKE_BASE_URL}/{FAKE_COURSE_STUB}/{REGISTER_USER_URL_STUB}",
        json={
            "api_key": FAKE_API_KEY,
            "api_secret": FAKE_API_SECRET,
            "catalog_id": FAKE_COURSE_STUB,
            "first_name": novoed_user.legal_address.first_name,
            "last_name": novoed_user.legal_address.last_name,
            "email": novoed_user.email,
            "external_id": str(novoed_user.id),
        },
    )
    assert result == (exp_created, exp_existing)
    enrollment.refresh_from_db()
    assert (enrollment.novoed_sync_date is not None) == exp_update_sync_date


@pytest.mark.django_db
def test_enroll_in_novoed_course_no_update(patched_post, novoed_user):
    """enroll_in_novoed_course should not update the NovoEd sync date if it has already been set"""
    dt = now_in_utc()
    enrollment = BootcampRunEnrollmentFactory.create(
        user=novoed_user,
        bootcamp_run__novoed_course_stub=FAKE_COURSE_STUB,
        novoed_sync_date=dt,
    )
    patched_post.return_value = MockResponse(
        content=None, status_code=status.HTTP_200_OK
    )
    enroll_in_novoed_course(novoed_user, FAKE_COURSE_STUB)
    enrollment.refresh_from_db()
    assert enrollment.novoed_sync_date == dt


@pytest.mark.django_db
def test_enroll_in_novoed_course_exc(patched_post, novoed_user):
    """
    enroll_in_novoed_course should raise if the response indicates an error
    """
    patched_post.return_value = MockResponse(
        content=None, status_code=status.HTTP_400_BAD_REQUEST
    )
    with pytest.raises(HTTPError):
        enroll_in_novoed_course(novoed_user, FAKE_COURSE_STUB)


@pytest.mark.django_db
def test_unenroll_from_novoed_course(patched_post, novoed_user):
    """unenroll_from_novoed_course should make a request to unenroll a user from a NovoEd course"""
    patched_post.return_value = MockResponse(
        content=None, status_code=status.HTTP_200_OK
    )
    unenroll_from_novoed_course(novoed_user, FAKE_COURSE_STUB)
    patched_post.assert_called_once_with(
        f"{FAKE_BASE_URL}/{FAKE_COURSE_STUB}/{UNENROLL_USER_URL_STUB}",
        json={
            "api_key": FAKE_API_KEY,
            "api_secret": FAKE_API_SECRET,
            "email": novoed_user.email,
        },
    )


@pytest.mark.django_db
def test_unenroll_from_novoed_course_exc(patched_post, novoed_user):
    """unenroll_from_novoed_course should raise if the response indicates an error"""
    patched_post.return_value = MockResponse(
        content=None, status_code=status.HTTP_400_BAD_REQUEST
    )
    with pytest.raises(HTTPError):
        unenroll_from_novoed_course(novoed_user, FAKE_COURSE_STUB)
