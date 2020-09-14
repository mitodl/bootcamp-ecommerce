"""tests for jobma functions"""
from urllib.parse import urljoin

from django.urls import reverse
import pytest

from jobma.api import create_interview_in_jobma, get_jobma_client
from jobma.factories import InterviewFactory


pytestmark = pytest.mark.django_db


def test_get_jobma_client(settings):
    """get_jobma_client should create a requests Session with relevant headers populated"""
    settings.JOBMA_ACCESS_TOKEN = "jobma_token"
    settings.VERSION = "9.8.7.6.5"
    settings.SITE_BASE_URL = "http://a.fake.url"
    session = get_jobma_client()
    assert session.headers["Authorization"] == f"Bearer {settings.JOBMA_ACCESS_TOKEN}"
    assert (
        session.headers["User-Agent"]
        == f"BootcampEcommerceBot/{settings.VERSION} ({settings.SITE_BASE_URL})"
    )


@pytest.mark.parametrize("interview_token", [None, "new token"])
@pytest.mark.parametrize("interview_url", [None, "https://new.url/"])
@pytest.mark.parametrize("preexisting_token", [None, "old token"])
@pytest.mark.parametrize("preexisting_url", [None, "http://old.url"])
def test_create_interview(
    mocker, settings, interview_token, interview_url, preexisting_token, preexisting_url
):  # pylint: disable=too-many-arguments
    """create_interview should send an existing interview to Jobma"""
    client_mock = mocker.patch("jobma.api.get_jobma_client")

    interview = InterviewFactory.create(
        interview_url=preexisting_url, interview_token=preexisting_token
    )
    settings.JOBMA_BASE_URL = "http://theothersiteurl.org"
    settings.SITE_BASE_URL = "http://thissitebaseurl.com"
    token = "anaccesstoken"
    settings.JOBMA_ACCESS_TOKEN = token

    response = {}
    if interview_url:
        response["interview_link"] = interview_url
    if interview_token:
        response["interview_token"] = interview_token
    client_mock.return_value.post.return_value.json.return_value = response

    create_interview_in_jobma(interview)
    client_mock.return_value.post.assert_called_once_with(
        "http://theothersiteurl.org/interviews",
        json={
            "interview_template_id": str(interview.job.interview_template_id),
            "job_id": str(interview.job.job_id),
            "job_code": interview.job.job_code,
            "job_title": interview.job.job_title,
            "callback_url": urljoin(
                settings.SITE_BASE_URL,
                reverse("jobma-webhook", kwargs={"pk": interview.id}),
            ),
            "candidate": {
                "first_name": interview.applicant.legal_address.first_name,
                "last_name": interview.applicant.legal_address.last_name,
                "phone": "",
                "email": interview.applicant.email,
            },
        },
    )
    client_mock.return_value.post.return_value.raise_for_status.assert_called_once_with()
    interview.refresh_from_db()

    expected_url = interview_url if interview_url else preexisting_url
    expected_token = interview_token if interview_token else preexisting_token

    assert interview.interview_url == expected_url
    assert interview.interview_token == expected_token
