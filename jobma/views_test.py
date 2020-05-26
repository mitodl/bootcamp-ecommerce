"""Jobma tests for views"""
from django.urls import reverse
import pytest
from rest_framework import status

from applications.constants import AppStates
from applications.factories import ApplicationStepSubmissionFactory
from jobma.constants import (
    COMPLETED,
    EXPIRED,
    PENDING,
    REJECTED,
)


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("jobma_status,expected_state_change", [
    (COMPLETED, True),
    (EXPIRED, True),
    (REJECTED, True),
    (PENDING, False),
])
def test_jobma_webhook(client, mocker, jobma_status, expected_state_change):
    """The jobma webhook view should check the access token, then update the interview status"""
    submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application__state=AppStates.AWAITING_USER_SUBMISSIONS.value
    )
    interview = submission.content_object.interview
    application = submission.bootcamp_application

    mocker.patch('jobma.permissions.JobmaWebhookPermission.has_permission', return_value=True)
    response = client.put(
        reverse('jobma-webhook', kwargs={"pk": interview.id}), content_type='application/json', data={
            "status": jobma_status,
            "results_url": "http://path/to/a/url"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    interview.refresh_from_db()
    assert interview.status == jobma_status

    application.refresh_from_db()
    assert application.state == (
        AppStates.AWAITING_SUBMISSION_REVIEW.value if expected_state_change else AppStates.AWAITING_USER_SUBMISSIONS.value
    )
