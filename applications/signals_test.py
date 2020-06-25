""" Tests for applications.signals"""
import pytest

from applications.factories import (
    BootcampApplicationFactory,
    ApplicationStepSubmissionFactory,
)

pytestmark = pytest.mark.django_db

# pylint: disable=redefined-outer-name


@pytest.fixture
def mock_hubspot(mocker):
    """ Mock sync_hubspot_application"""
    return mocker.patch("applications.signals.sync_hubspot_application")


def test_application_signal(mock_hubspot):
    """Test that hubspot is synced whenever a BootcampApplication is created/updated"""

    application = BootcampApplicationFactory.create()
    application.save()
    application.save()
    assert mock_hubspot.call_count == 2  # None for creation, twice for updates
    mock_hubspot.assert_any_call(application)


def test_submission_signal(mock_hubspot):
    """ Test that hubspot is synced whenever an ApplicationStepSubmission is created"""

    submission = ApplicationStepSubmissionFactory.create()
    submission.run_application_step.bootcamp_run = (
        submission.bootcamp_application.bootcamp_run
    )
    submission.save()
    submission.save()
    assert mock_hubspot.call_count == 1  # Once for submission creation
    mock_hubspot.assert_any_call(submission.bootcamp_application)
