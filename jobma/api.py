"""functions relating to Jobma"""
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from requests import Session


def get_jobma_client():
    """
    Get an authenticated client for use with Jobma APIs

    Returns:
        Session: A Jobma session object
    """
    session = Session()
    session.headers["Authorization"] = f"Bearer {settings.JOBMA_ACCESS_TOKEN}"
    return session


def create_interview(interview):
    """
    Create a new interview on Jobma

    Args:
        interview (Interview): An interview object
    """
    client = get_jobma_client()
    url = urljoin(settings.JOBMA_BASE_URL, "interviews")
    response = client.post(url, json={
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
    response.raise_for_status()
    result = response.json()
    interview.interview_id = result["interview_id"]
    interview.save_and_log(None)

    # Now we wait for the postback
