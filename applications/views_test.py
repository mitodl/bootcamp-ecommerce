"""Tests for bootcamp application views"""
from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from applications.constants import (
    AppStates,
    REVIEW_STATUS_REJECTED,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_PENDING,
    ALL_REVIEW_STATUSES,
    SUBMISSION_STATUS_SUBMITTED,
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
    ApplicantLetterFactory,
    QuizSubmissionFactory,
    VideoInterviewSubmissionFactory,
)
from applications.serializers import (
    BootcampApplicationDetailSerializer,
    BootcampApplicationSerializer,
    SubmissionReviewSerializer,
)
from applications.views import BootcampApplicationViewset
from ecommerce.factories import OrderFactory
from ecommerce.models import Order
from ecommerce.serializers import ApplicationOrderSerializer
from klasses.factories import BootcampRunFactory
from main.test_utils import assert_drf_json_equal
from main.utils import serializer_date_format, now_in_utc
from profiles.factories import UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def bootcamp_run_submissions():
    """ Generate bootcamp runs and submissions """
    bootcamp_runs = BootcampRunFactory.create_batch(3)
    submissions = []
    for bootcamp_run in bootcamp_runs:
        application_step = BootcampRunApplicationStepFactory(
            bootcamp_run=bootcamp_run, application_step__bootcamp=bootcamp_run.bootcamp
        )
        for review_status in ALL_REVIEW_STATUSES:
            submissions.append(
                ApplicationStepSubmissionFactory.create(
                    review_status=review_status,
                    bootcamp_application__bootcamp_run=bootcamp_run,
                    run_application_step=application_step,
                    content_object=VideoInterviewSubmissionFactory.create(),
                    is_review_ready=True,
                )
            )
    return SimpleNamespace(bootcamp_runs=bootcamp_runs, submissions=submissions)


@pytest.mark.parametrize(
    "action,exp_serializer",
    [
        ["retrieve", BootcampApplicationDetailSerializer],
        ["list", BootcampApplicationSerializer],
        ["create", BootcampApplicationSerializer],
    ],
)
def test_view_serializer(mocker, action, exp_serializer):
    """The bootcamp application view should use the expected serializer depending on the action"""
    serializer_cls = BootcampApplicationViewset.get_serializer_class(
        mocker.Mock(action=action)
    )
    assert serializer_cls == exp_serializer


# pylint: disable=redefined-outer-name, too-many-arguments
def test_view_serializer_context(mocker):
    """
    The bootcamp application view should add context to the serializer in the list view
    """
    application = BootcampApplicationFactory.create()
    patched_serializer = mocker.patch(
        "applications.views.BootcampApplicationSerializer",
        return_value=mocker.Mock(data={"key": "value"}),
    )
    view = BootcampApplicationViewset.as_view({"get": "list"})
    factory = APIRequestFactory()
    request = factory.get(reverse("applications_api-list"))
    force_authenticate(request, user=application.user)
    view(request).render()
    serializer_context = patched_serializer.call_args_list[0][1]["context"]
    assert "include_page" in serializer_context
    assert serializer_context["include_page"] is True


def test_app_detail_view(client):
    """The bootcamp application detail view should return a successful response"""
    application = BootcampApplicationFactory.create()
    client.force_login(application.user)
    url = reverse("applications_api-detail", kwargs={"pk": application.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == application.id


def test_app_list_view(client):
    """
    The bootcamp application list view should return a successful response, and should not include
    other user's applications in the response data
    """
    applications = BootcampApplicationFactory.create_batch(2)
    client.force_login(applications[0].user)
    url = reverse("applications_api-list")
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    resp_json = resp.json()
    assert len(resp_json) == 1
    assert resp_json[0]["id"] == applications[0].id


def test_app_create_view(client):
    """The bootcamp application create view should return a successful response"""
    bootcamp_run = BootcampRunFactory.create()
    user = UserFactory.create()
    client.force_login(user)
    url = reverse("applications_api-list")
    resp = client.post(url, data={"bootcamp_run_id": bootcamp_run.id})
    assert resp.status_code == status.HTTP_201_CREATED
    application_id = resp.json()["id"]
    # Making a request for an existing application should return a 200 instead of a 201
    resp = client.post(url, data={"bootcamp_run_id": bootcamp_run.id})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == application_id


def test_app_detail_view_permissions(client):
    """
    The bootcamp application detail view should return an error if the user is not logged in or
    is requesting an application that isn't their own
    """
    application = BootcampApplicationFactory.create()
    url = reverse("applications_api-detail", kwargs={"pk": application.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN

    other_user_application = BootcampApplicationFactory.create()
    client.force_login(application.user)
    url = reverse("applications_api-detail", kwargs={"pk": other_user_application.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "review_status, application_state",
    [
        (REVIEW_STATUS_APPROVED, AppStates.AWAITING_PAYMENT.value),
        (REVIEW_STATUS_REJECTED, AppStates.REJECTED.value),
    ],
)
def test_review_submission_update(admin_drf_client, review_status, application_state):
    """
    The review submission view should return successful response, and update review_status and application
    """
    bootcamp_application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_SUBMISSION_REVIEW.value
    )
    submission = ApplicationStepSubmissionFactory.create(
        is_pending=True,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
        submission_status=SUBMISSION_STATUS_SUBMITTED,
    )
    url = reverse("submissions_api-detail", kwargs={"pk": submission.id})
    resp = admin_drf_client.patch(url, data={"review_status": review_status})
    assert resp.status_code == status.HTTP_200_OK
    submission.refresh_from_db()
    assert submission.review_status == review_status
    assert submission.bootcamp_application.state == application_state


@pytest.mark.parametrize(
    "submission_factory", [QuizSubmissionFactory, VideoInterviewSubmissionFactory]
)
def test_review_submission_list(
    admin_drf_client, submission_factory, bootcamp_run_submissions
):
    """
    The review submission list view should return a list of all submissions
    """
    url = reverse("submissions_api-list")
    resp = admin_drf_client.get(url, dict(limit=100))
    assert resp.status_code == status.HTTP_200_OK
    result = resp.json()
    result["facets"]["review_statuses"] = sorted(
        result["facets"]["review_statuses"], key=lambda s: s["review_status"]
    )

    assert result == {
        "count": len(bootcamp_run_submissions.submissions),
        "next": None,
        "previous": None,
        "results": [
            SubmissionReviewSerializer(instance=submission).data
            for submission in sorted(
                bootcamp_run_submissions.submissions, key=lambda s: s.id
            )
        ],
        "facets": {
            "bootcamp_runs": [
                {
                    "id": bootcamp_run.id,
                    "title": bootcamp_run.title,
                    "start_date": serializer_date_format(bootcamp_run.start_date),
                    "end_date": serializer_date_format(bootcamp_run.end_date),
                    "count": 4,
                }
                for bootcamp_run in sorted(
                    bootcamp_run_submissions.bootcamp_runs, key=lambda b: b.id
                )
            ],
            "review_statuses": [
                {
                    "review_status": review_status,
                    "count": len(bootcamp_run_submissions.bootcamp_runs),
                }
                for review_status in sorted(ALL_REVIEW_STATUSES)
            ],
        },
    }


def test_review_submission_list_expired(admin_drf_client, bootcamp_run_submissions):
    """
    The review submission list view should not return submissions if run ended
    """
    for run in bootcamp_run_submissions.bootcamp_runs:
        run.end_date = now_in_utc() - timedelta(weeks=1)
        run.save()
    url = reverse("submissions_api-list")
    resp = admin_drf_client.get(url, dict(limit=100))
    assert resp.status_code == status.HTTP_200_OK
    result = resp.json()
    assert result == {
        "count": 0,
        "next": None,
        "previous": None,
        "results": [],
        "facets": {"bootcamp_runs": [], "review_statuses": []},
    }


def test_review_submission_list_query_bootcamp_run_id(admin_drf_client):
    """
    The review submission list view should return a list of submissions filtered by bootcamp run id
    """
    submission = ApplicationStepSubmissionFactory.create(is_review_ready=True)
    bootcamp_run = submission.bootcamp_application.bootcamp_run
    ApplicationStepSubmissionFactory.create_batch(3)
    url = reverse("submissions_api-list")
    resp = admin_drf_client.get(url, {"bootcamp_run_id": bootcamp_run.id})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [SubmissionReviewSerializer(instance=submission).data],
        "facets": {
            "bootcamp_runs": [
                {
                    "id": bootcamp_run.id,
                    "title": bootcamp_run.title,
                    "start_date": serializer_date_format(bootcamp_run.start_date),
                    "end_date": serializer_date_format(bootcamp_run.end_date),
                    "count": 1,
                }
            ],
            "review_statuses": [
                {"review_status": submission.review_status, "count": 1}
            ],
        },
    }


@pytest.mark.parametrize("review_status", ALL_REVIEW_STATUSES)
def test_review_submission_list_query_review_status(admin_drf_client, review_status):
    """
    The review submission list view should return a list of submissions filtered by review status
    """
    # Create a few submissions that should be filtered out due to submission status or application state
    ApplicationStepSubmissionFactory.create(is_pending=True)
    ApplicationStepSubmissionFactory.create(is_approved=True)
    ApplicationStepSubmissionFactory.create(is_rejected=True)
    ApplicationStepSubmissionFactory.create(is_waitlisted=True)
    ApplicationStepSubmissionFactory.create(
        is_approved=True,
        submission_status=SUBMISSION_STATUS_SUBMITTED,
        bootcamp_application=BootcampApplicationFactory.create(state="AWAITING_RESUME"),
    )

    # Create a few submissions that should be included in results
    submissions = [
        ApplicationStepSubmissionFactory.create(is_pending=True, is_review_ready=True),
        ApplicationStepSubmissionFactory.create(is_approved=True, is_review_ready=True),
        ApplicationStepSubmissionFactory.create(is_rejected=True, is_review_ready=True),
        ApplicationStepSubmissionFactory.create(
            is_waitlisted=True, is_review_ready=True
        ),
    ]
    submission = next(filter(lambda s: s.review_status == review_status, submissions))
    bootcamp_run = submission.bootcamp_application.bootcamp_run
    url = reverse("submissions_api-list")
    resp = admin_drf_client.get(url, {"review_status": review_status})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        "count": 1,
        "next": None,
        "previous": None,
        "results": [SubmissionReviewSerializer(instance=submission).data],
        "facets": {
            "bootcamp_runs": [
                {
                    "id": bootcamp_run.id,
                    "title": bootcamp_run.title,
                    "start_date": serializer_date_format(bootcamp_run.start_date),
                    "end_date": serializer_date_format(bootcamp_run.end_date),
                    "count": 1,
                }
            ],
            "review_statuses": [
                {"review_status": submission.review_status, "count": 1}
            ],
        },
    }


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
def test_review_submission_list_query_review_status_in(
    admin_drf_client, review_statuses
):
    """
    The review submission list view should return a list of all submissions filtered by multiple review statuses
    """
    submissions = [
        ApplicationStepSubmissionFactory.create(is_pending=True, is_review_ready=True),
        ApplicationStepSubmissionFactory.create(is_approved=True, is_review_ready=True),
        ApplicationStepSubmissionFactory.create(is_rejected=True, is_review_ready=True),
    ]
    submissions = list(
        filter(lambda s: s.review_status in review_statuses, submissions)
    )
    bootcamp_runs = [
        submission.bootcamp_application.bootcamp_run for submission in submissions
    ]
    url = reverse("submissions_api-list")
    resp = admin_drf_client.get(url, {"review_status__in": ",".join(review_statuses)})
    assert resp.status_code == status.HTTP_200_OK
    json = resp.json()
    json["results"] = sorted(json["results"], key=lambda s: s["id"])
    json["facets"]["bootcamp_runs"] = sorted(
        json["facets"]["bootcamp_runs"], key=lambda b: b["id"]
    )
    json["facets"]["review_statuses"] = sorted(
        json["facets"]["review_statuses"], key=lambda s: s["review_status"]
    )
    assert json == {
        "count": len(review_statuses),
        "next": None,
        "previous": None,
        "results": [
            SubmissionReviewSerializer(instance=submission).data
            for submission in sorted(submissions, key=lambda s: s.id)
        ],
        "facets": {
            "bootcamp_runs": [
                {
                    "id": bootcamp_run.id,
                    "title": bootcamp_run.title,
                    "start_date": serializer_date_format(bootcamp_run.start_date),
                    "end_date": serializer_date_format(bootcamp_run.end_date),
                    "count": 1,
                }
                for bootcamp_run in sorted(bootcamp_runs, key=lambda b: b.id)
            ],
            "review_statuses": [
                {"review_status": submission.review_status, "count": 1}
                for submission in sorted(submissions, key=lambda s: s.review_status)
            ],
        },
    }


@pytest.mark.parametrize(
    "has_resume,has_linkedin,resp_status",
    [
        [True, True, status.HTTP_200_OK],
        [False, True, status.HTTP_200_OK],
        [True, False, status.HTTP_200_OK],
        [False, False, status.HTTP_400_BAD_REQUEST],
    ],
)
def test_upload_resume_view(client, mocker, has_resume, has_linkedin, resp_status):
    """
    Upload resume view should return successful response, and update application state
    """
    mocker.patch(
        "applications.views.UserIsOwnerPermission.has_permission", return_value=True
    )
    bootcamp_application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_RESUME.value
    )
    client.force_login(bootcamp_application.user)

    url = reverse("upload-resume", kwargs={"pk": bootcamp_application.id})
    data = {}
    if has_linkedin:
        data["linkedin_url"] = "some_url"
    if has_resume:
        resume_file = SimpleUploadedFile("resume.pdf", b"file_content")
        data["file"] = resume_file
    resp = client.post(url, data)

    assert resp.status_code == resp_status
    bootcamp_application.refresh_from_db()
    if has_resume or has_linkedin:
        assert bootcamp_application.state == AppStates.AWAITING_USER_SUBMISSIONS.value
    else:
        assert bootcamp_application.state == AppStates.AWAITING_RESUME.value

    if has_resume:
        assert resume_file.name in bootcamp_application.resume_file.name


def test_application_detail_queryset_orders(client):
    """
    Test that the application detail queryset filters orders
    """
    application = BootcampApplicationFactory.create()
    user = application.user
    OrderFactory.create(application=application, user=user, status=Order.CREATED)
    fulfilled_order = OrderFactory.create(
        application=application, user=user, status=Order.FULFILLED
    )

    client.force_login(user)
    resp = client.get(reverse("applications_api-detail", kwargs={"pk": application.id}))
    rendered_orders = resp.json()["orders"]
    assert_drf_json_equal(
        rendered_orders, [ApplicationOrderSerializer(fulfilled_order).data]
    )


def test_letters_view(client):
    """Any user, including anonymous users, should be able to view the letter if they have the right UUID"""
    letter = ApplicantLetterFactory.create()
    resp = client.get(reverse("letters", kwargs={"hash": letter.hash}))
    assert resp.status_code == status.HTTP_200_OK
    assert letter.letter_text in resp.content.decode()
