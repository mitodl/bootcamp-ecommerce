"""Applications filters"""

import pytest

from applications.constants import (
    ALL_REVIEW_STATUSES,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    REVIEW_STATUS_REJECTED,
)
from applications.factories import ApplicationStepSubmissionFactory
from applications.filters import ApplicationStepSubmissionFilterSet
from applications.models import ApplicationStepSubmission

pytestmark = pytest.mark.django_db


def test_application_step_submission_filterset_bootcamp_id():
    """Verify that ApplicationStepSubmissionFilterSet's bootcamp_id filter works"""
    matching = ApplicationStepSubmissionFactory.create()
    nonmatching = ApplicationStepSubmissionFactory.create()

    params = {"bootcamp_run_id": matching.bootcamp_application.bootcamp_run.id}

    query = ApplicationStepSubmissionFilterSet(
        params, queryset=ApplicationStepSubmission.objects.all()
    ).qs

    assert matching in query
    assert nonmatching not in query


@pytest.mark.parametrize("review_status", ALL_REVIEW_STATUSES)
def test_application_step_submission_filterset_review_status_exact(review_status):
    """Verify that ApplicationStepSubmissionFilterSet's review_status (exact) filter works"""
    submissions = [
        ApplicationStepSubmissionFactory.create(is_pending=True),
        ApplicationStepSubmissionFactory.create(is_approved=True),
        ApplicationStepSubmissionFactory.create(is_rejected=True),
        ApplicationStepSubmissionFactory.create(is_waitlisted=True),
    ]

    params = {"review_status": review_status}

    query = ApplicationStepSubmissionFilterSet(
        params, queryset=ApplicationStepSubmission.objects.all()
    ).qs

    assert len(query) == 1

    for submission in submissions:
        if submission.review_status == review_status:
            assert submission in query
        else:
            assert submission not in query


@pytest.mark.parametrize(
    "review_statuses",
    [
        [REVIEW_STATUS_PENDING],
        [REVIEW_STATUS_APPROVED],
        [REVIEW_STATUS_REJECTED],
        [REVIEW_STATUS_PENDING, REVIEW_STATUS_APPROVED],
        [REVIEW_STATUS_APPROVED, REVIEW_STATUS_REJECTED],
        [REVIEW_STATUS_REJECTED, REVIEW_STATUS_PENDING],
        [REVIEW_STATUS_REJECTED, REVIEW_STATUS_APPROVED, REVIEW_STATUS_PENDING],
    ],
)
def test_application_step_submission_filterset_review_status_in(review_statuses):
    """Verify that ApplicationStepSubmissionFilterSet's review_status__in filter works"""
    submissions = [
        ApplicationStepSubmissionFactory.create(is_pending=True),
        ApplicationStepSubmissionFactory.create(is_approved=True),
        ApplicationStepSubmissionFactory.create(is_rejected=True),
    ]

    params = {"review_status__in": ",".join(review_statuses)}

    query = ApplicationStepSubmissionFilterSet(
        params, queryset=ApplicationStepSubmission.objects.all()
    ).qs

    assert len(query) == len(review_statuses)

    for submission in submissions:
        if submission.review_status in review_statuses:
            assert submission in query
        else:
            assert submission not in query
