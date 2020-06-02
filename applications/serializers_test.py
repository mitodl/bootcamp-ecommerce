"""Tests for bootcamp application serializers"""
# pylint: disable=redefined-outer-name
from datetime import timedelta
from types import SimpleNamespace

import pytest
import factory

from applications.constants import (
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    AppStates,
)
from applications.serializers import (
    BootcampApplicationDetailSerializer,
    BootcampRunStepSerializer,
    SubmissionSerializer,
    BootcampApplicationSerializer,
    SubmissionReviewSerializer,
)
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
    ApplicationStepFactory,
)
from ecommerce.factories import OrderFactory
from ecommerce.models import Order
from ecommerce.serializers import ApplicationOrderSerializer
from klasses.factories import BootcampRunFactory, InstallmentFactory
from klasses.serializers import BootcampRunSerializer
from main.test_utils import serializer_date_format
from main.utils import now_in_utc
from profiles.factories import UserFactory
from profiles.serializers import UserSerializer


@pytest.fixture
def app_data():
    """Fixture for a bootcamp application and related data"""
    bootcamp_run = BootcampRunFactory.create()
    run_steps = BootcampRunApplicationStepFactory.create_batch(
        2, bootcamp_run=bootcamp_run
    )
    application = BootcampApplicationFactory(bootcamp_run=bootcamp_run)
    return SimpleNamespace(application=application, run_steps=run_steps)


@pytest.mark.django_db
def test_application_detail_serializer(app_data):
    """
    BootcampApplicationDetailSerializer should return a serialized version of a bootcamp application
    with related data
    """
    application = app_data.application
    data = BootcampApplicationDetailSerializer(instance=application).data
    assert data == {
        "id": application.id,
        "bootcamp_run_id": application.bootcamp_run_id,
        "state": application.state,
        "resume_filename": None,
        "linkedin_url": None,
        "resume_upload_date": serializer_date_format(application.resume_upload_date),
        "payment_deadline": None,
        "created_on": serializer_date_format(application.created_on),
        "run_application_steps": BootcampRunStepSerializer(
            instance=app_data.run_steps, many=True
        ).data,
        "submissions": [],
        "orders": [],
    }


@pytest.mark.django_db
def test_app_detail_serializer_deadline(app_data):
    """
    BootcampApplicationDetailSerializer results should include a payment deadline based on the
    bootcamp run installments
    """
    application = app_data.application
    installments = InstallmentFactory.create_batch(
        2,
        bootcamp_run=application.bootcamp_run,
        deadline=factory.Iterator([now_in_utc(), (now_in_utc() + timedelta(days=1))]),
    )
    data = BootcampApplicationDetailSerializer(instance=application).data
    assert data["payment_deadline"] == serializer_date_format(installments[1].deadline)


@pytest.mark.django_db
def test_application_detail_serializer_nested(app_data):
    """
    BootcampApplicationDetailSerializer results should include nested submission and order data
    """
    application = app_data.application
    submissions = ApplicationStepSubmissionFactory.create_batch(
        2,
        bootcamp_application=application,
        run_application_step=factory.Iterator(app_data.run_steps),
    )
    orders = OrderFactory.create_batch(
        2, application=application, status=Order.FULFILLED
    )
    data = BootcampApplicationDetailSerializer(instance=application).data
    assert (
        data["submissions"]
        == SubmissionSerializer(instance=submissions, many=True).data
    )
    assert data["orders"] == ApplicationOrderSerializer(instance=orders, many=True).data


@pytest.mark.django_db
def test_application_list_serializer(app_data):
    """
    BootcampApplicationListSerializer should return serialized versions of all of a user's
    bootcamp applications
    """
    other_app = BootcampApplicationFactory.create(user=app_data.application.user)
    user_applications = [app_data.application, other_app]
    data = BootcampApplicationSerializer(instance=user_applications, many=True).data
    assert data == [
        {
            "id": application.id,
            "state": application.state,
            "created_on": serializer_date_format(application.created_on),
            "bootcamp_run": BootcampRunSerializer(
                instance=application.bootcamp_run
            ).data,
        }
        for application in user_applications
    ]


def test_bootcamp_run_step_serializer():
    """
    BootcampRunStepSerializer should serialize a bootcamp run application step with expected fields
    """
    app_step = ApplicationStepFactory.build()
    run_step = BootcampRunApplicationStepFactory.build(application_step=app_step)
    data = BootcampRunStepSerializer(instance=run_step).data
    assert data == {
        "id": None,
        "due_date": serializer_date_format(run_step.due_date),
        "step_order": app_step.step_order,
        "submission_type": app_step.submission_type,
    }


def test_submission_serializer():
    """
    SubmissionSerializer should serialize an application submission with expected fields
    """
    run_step = BootcampRunApplicationStepFactory.build(id=123)
    submission = ApplicationStepSubmissionFactory.build(run_application_step=run_step)
    data = SubmissionSerializer(instance=submission).data
    assert data == {
        "id": None,
        "run_application_step_id": 123,
        "submitted_date": serializer_date_format(submission.submitted_date),
        "review_status": submission.review_status,
        "review_status_date": serializer_date_format(submission.review_status_date),
    }


@pytest.mark.django_db
def test_submission_review_serializer():
    """Test SubmissionReviewSerializer"""
    user = UserFactory.create()
    run_step = BootcampRunApplicationStepFactory.create()
    submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application__user=user, run_application_step=run_step
    )
    data = SubmissionReviewSerializer(instance=submission).data
    assert data == {
        "id": submission.id,
        "run_application_step_id": run_step.id,
        "submitted_date": serializer_date_format(submission.submitted_date),
        "review_status": submission.review_status,
        "review_status_date": serializer_date_format(submission.review_status_date),
        "learner": UserSerializer(instance=user).data,
        "bootcamp_application": BootcampApplicationSerializer(
            instance=submission.bootcamp_application
        ).data,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "review,other_submissions,other_steps,expected",
    [
        (REVIEW_STATUS_APPROVED, True, True, AppStates.AWAITING_USER_SUBMISSIONS.value),
        (
            REVIEW_STATUS_APPROVED,
            False,
            True,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
        ),
        (REVIEW_STATUS_APPROVED, False, False, AppStates.AWAITING_PAYMENT.value),
        (REVIEW_STATUS_REJECTED, False, False, AppStates.REJECTED.value),
    ],
)
def test_submission_review_serializer_update(
    review, other_submissions, other_steps, expected
):
    """Test SubmissionReviewSerializer update()"""
    bootcamp_application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_SUBMISSION_REVIEW.value
    )
    submission = ApplicationStepSubmissionFactory.create(
        is_pending=True,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
    )
    if other_submissions:
        application_step = BootcampRunApplicationStepFactory.create(
            bootcamp_run=bootcamp_application.bootcamp_run,
            application_step__bootcamp=bootcamp_application.bootcamp_run.bootcamp,
        )
        ApplicationStepSubmissionFactory.create(
            is_pending=True,
            bootcamp_application=bootcamp_application,
            run_application_step=application_step,
        )
    if other_steps:
        BootcampRunApplicationStepFactory.create(
            bootcamp_run=bootcamp_application.bootcamp_run
        )

    serializer = SubmissionReviewSerializer(submission, {"review_status": review})
    serializer.is_valid()

    assert serializer.errors == {}

    serializer.save()

    bootcamp_application.refresh_from_db()
    submission.refresh_from_db()

    assert submission.review_status == review
    assert bootcamp_application.state == expected
