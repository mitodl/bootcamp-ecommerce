"""Tests for bootcamp application views"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from applications.constants import (
    AppStates,
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
)
from applications.factories import (
    BootcampApplicationFactory,
    ApplicationStepSubmissionFactory,
)
from applications.serializers import (
    BootcampApplicationDetailSerializer,
    BootcampApplicationSerializer,
)
from applications.views import BootcampApplicationViewset
from klasses.factories import BootcampRunFactory
from profiles.factories import UserFactory


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


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_app_detail_view(client):
    """The bootcamp application detail view should return a successful response"""
    application = BootcampApplicationFactory.create()
    client.force_login(application.user)
    url = reverse("applications_api-detail", kwargs={"pk": application.id})
    resp = client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["id"] == application.id


@pytest.mark.django_db
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


@pytest.mark.django_db
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


@pytest.mark.django_db
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
    "review_status", [REVIEW_STATUS_APPROVED, REVIEW_STATUS_REJECTED]
)
@pytest.mark.django_db
def test_review_submission_update(client, mocker, review_status):
    """
    The review submission view should return successful response, and update review_status
    """
    mocker.patch("applications.views.IsAdminUser.has_permission", return_value=True)
    bootcamp_application = BootcampApplicationFactory(
        state=AppStates.AWAITING_SUBMISSION_REVIEW.value
    )
    submission = ApplicationStepSubmissionFactory(
        review_status=None,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
    )
    url = reverse("submit-review", kwargs={"pk": submission.id})
    resp = client.patch(
        url, content_type="application/json", data={"review_status": review_status}
    )
    assert resp.status_code == status.HTTP_200_OK
    submission.refresh_from_db()
    assert submission.review_status == review_status


@pytest.mark.parametrize(
    "has_resume,has_linkedin,state", [
        [True, True, AppStates.AWAITING_USER_SUBMISSIONS.value],
        [False, True, AppStates.AWAITING_USER_SUBMISSIONS.value],
        [True, False, AppStates.AWAITING_USER_SUBMISSIONS.value],
])
@pytest.mark.django_db
def test_upload_resume_view(client, mocker, has_resume, has_linkedin, state):
    """
    Upload resume view should return successful response, and update application state
    """
    mocker.patch('applications.views.UserIsOwnerPermission.has_permission', return_value=True)
    bootcamp_application = BootcampApplicationFactory.create(state=AppStates.AWAITING_RESUME.value)
    client.force_login(bootcamp_application.user)

    url = reverse("upload-resume", kwargs={"pk": bootcamp_application.id})
    data = {}
    if has_linkedin:
        data['linkedin_url'] = "some_url"
    if has_resume:
        resume_file = SimpleUploadedFile("resume.pdf", b'file_content')
        data['file'] = resume_file
    resp = client.post(url, data)
    assert resp.status_code == status.HTTP_200_OK
    bootcamp_application.refresh_from_db()
    assert bootcamp_application.state == state

    if has_resume:
        assert resume_file.name in bootcamp_application.resume_file.name
