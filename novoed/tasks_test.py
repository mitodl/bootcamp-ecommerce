# pylint: disable=redefined-outer-name
"""NovoEd task tests"""

import pytest

from novoed.tasks import enroll_users_in_novoed_course, unenroll_user_from_novoed_course
from profiles.factories import UserFactory

pytestmark = pytest.mark.django_db
FAKE_COURSE_STUB = "my-course"


@pytest.fixture
def patched_novoed_api(mocker):
    """Patches NovoEd API functionality"""
    return mocker.patch("novoed.tasks.api")


def test_enroll_users_in_novoed_course(patched_novoed_api):
    """enroll_users_in_novoed_course should call the API function to enroll each user indicated by the given IDs"""
    users = UserFactory.create_batch(2)
    user_ids = [user.id for user in users]
    enroll_users_in_novoed_course.delay(
        user_ids=user_ids, novoed_course_stub=FAKE_COURSE_STUB
    )
    assert patched_novoed_api.enroll_in_novoed_course.call_count == len(users)
    for user in users:
        patched_novoed_api.enroll_in_novoed_course.assert_any_call(
            user, FAKE_COURSE_STUB
        )


def test_unenroll_user_from_novoed_course(patched_novoed_api):
    """unenroll_user_from_novoed_course should call the API function to unenroll a user indicated by the given ID"""
    user = UserFactory.create()
    unenroll_user_from_novoed_course.delay(
        user_id=user.id, novoed_course_stub=FAKE_COURSE_STUB
    )
    patched_novoed_api.unenroll_from_novoed_course.assert_called_once_with(
        user, FAKE_COURSE_STUB
    )
