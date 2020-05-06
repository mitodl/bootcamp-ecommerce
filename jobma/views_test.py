"""Jobma tests for views"""
from django.urls import reverse
import pytest
from rest_framework import status

from jobma.factories import InterviewFactory


pytestmark = pytest.mark.django_db


def test_jobma_webhook(client, mocker):
    """The jobma webhook view should check the access token, then update the interview status"""
    interview = InterviewFactory.create()
    new_interview_status = "completed"

    mocker.patch('jobma.permissions.JobmaWebhookPermission.has_permission', return_value=True)
    response = client.put(
        reverse('jobma-webhook', kwargs={"pk": interview.id}), content_type='application/json', data={
            "status": new_interview_status,
            "results_url": "http://path/to/a/url"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    interview.refresh_from_db()
    assert interview.status == new_interview_status
