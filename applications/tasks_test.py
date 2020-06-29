"""Tests for application tasks"""

import pytest


from applications.tasks import create_and_send_applicant_letter
from ecommerce.test_utils import create_test_application


pytestmark = pytest.mark.django_db


@pytest.fixture
def application():
    """An application for testing"""
    yield create_test_application()


def test_create_and_send_applicant_letter(
    mocker, application
):  # pylint: disable=redefined-outer-name
    """This should just start a task to forward the request to the API function"""
    letter_type = "letter_type"
    patched = mocker.patch("applications.mail_api.create_and_send_applicant_letter")

    create_and_send_applicant_letter.delay(
        application_id=application.id, letter_type=letter_type
    )
    patched.assert_called_once_with(application, letter_type=letter_type)
