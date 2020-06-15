"""functions relating to Jobma"""
import logging
from urllib.parse import urljoin

from django.conf import settings
from django.urls import reverse
from requests import Session


log = logging.getLogger(__name__)


def get_jobma_client():
    """
    Get an authenticated client for use with Jobma APIs

    Returns:
        Session: A Jobma session object
    """
    session = Session()
    session.headers["Authorization"] = f"Bearer {settings.JOBMA_ACCESS_TOKEN}"
    session.headers[
        "User-Agent"
    ] = f"BootcampEcommerceBot/{settings.VERSION} ({settings.SITE_BASE_URL})"
    return session


def create_interview(interview):
    """
    Create a new interview on Jobma

    Args:
        interview (Interview): An interview object
    """
    client = get_jobma_client()
    url = urljoin(settings.JOBMA_BASE_URL, "interviews")
    job = interview.job
    first_name, last_name = interview.applicant.profile.first_and_last_names
    response = client.post(
        url,
        json={
            "interview_template_id": str(job.interview_template_id),
            "job_id": str(job.job_id),
            "job_code": job.job_code,
            "job_title": job.job_title,
            "callback_url": urljoin(
                settings.SITE_BASE_URL,
                reverse("jobma-webhook", kwargs={"pk": interview.id}),
            ),
            "candidate": {
                "first_name": first_name,
                "last_name": last_name,
                "phone": "",
                "email": interview.applicant.email,
            },
        },
    )
    response.raise_for_status()
    result = response.json()
    interview_link = result.get("interview_link")
    if interview_link is not None:
        interview.interview_url = result["interview_link"]
        interview.save_and_log(None)
    else:
        log.error("Interview link not found in payload - %s", result)

    return interview_link
