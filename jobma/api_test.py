"""tests for jobma functions"""
from urllib.parse import urljoin

from django.urls import reverse
import pytest

from jobma.api import create_interview
from jobma.factories import InterviewFactory


pytestmark = pytest.mark.django_db


def test_create_interview(mocker, settings):
    """create_interview should send an existing interview to Jobma"""
    client_mock = mocker.patch('jobma.api.get_jobma_client')
    new_interview_id = 987654321
    client_mock.return_value.post.return_value.json.return_value = {"interview_id": str(new_interview_id)}

    interview = InterviewFactory.create()
    settings.JOBMA_BASE_URL = "http://theothersiteurl.org"
    settings.SITE_BASE_URL = "http://thissitebaseurl.com"
    token = "anaccesstoken"
    settings.JOBMA_ACCESS_TOKEN = token

    create_interview(interview)
    client_mock.return_value.post.assert_called_once_with("http://theothersiteurl.org/interviews", json={
        "interview_template_id": str(interview.job.interview_template_id),
        "job_id": str(interview.job.job_id),
        "job_code": interview.job.job_code,
        "job_title": interview.job.job_title,
        "callback_url": urljoin(
            settings.SITE_BASE_URL,
            reverse("jobma-webhook", kwargs={"pk": interview.id}),
        ),
        "candidate": {
            "first_name": interview.candidate_first_name,
            "last_name": interview.candidate_last_name,
            "phone": interview.candidate_phone,
            "email": interview.candidate_email,
        },
    })
    client_mock.return_value.post.return_value.raise_for_status.assert_called_once_with()
    interview.refresh_from_db()
    assert interview.interview_id == new_interview_id
