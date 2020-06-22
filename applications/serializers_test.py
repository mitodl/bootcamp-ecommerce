"""Tests for bootcamp application serializers"""
# pylint: disable=redefined-outer-name
from datetime import timedelta
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
import pytest
import factory

from applications.constants import (
    REVIEW_STATUS_APPROVED,
    REVIEW_STATUS_REJECTED,
    AppStates,
    REVIEW_STATUS_WAITLISTED,
    REVIEW_STATUS_PENDING,
)
from applications.exceptions import InvalidApplicationStateException
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
    VideoInterviewSubmissionFactory,
)
from ecommerce.factories import OrderFactory
from ecommerce.models import Order
from ecommerce.serializers import ApplicationOrderSerializer
from jobma.factories import InterviewFactory
from klasses.factories import BootcampRunFactory, InstallmentFactory
from klasses.serializers import BootcampRunSerializer
from main.test_utils import serializer_date_format
from profiles.factories import UserFactory
from profiles.serializers import UserSerializer


pytestmark = pytest.mark.django_db


@pytest.fixture
def app_data():
    """Fixture for a bootcamp application and related data"""
    bootcamp_run = BootcampRunFactory.create()
    installment = InstallmentFactory.create(bootcamp_run=bootcamp_run, amount=0)
    run_steps = BootcampRunApplicationStepFactory.create_batch(
        2, bootcamp_run=bootcamp_run
    )
    application = BootcampApplicationFactory(bootcamp_run=bootcamp_run)
    application.resume_file = SimpleUploadedFile(
        "resume.txt", b"these are the file contents!"
    )
    application.save()
    return SimpleNamespace(
        application=application, installment=installment, run_steps=run_steps
    )


@pytest.mark.parametrize("has_resume", [True, False])
def test_application_detail_serializer(app_data, has_resume):
    """
    BootcampApplicationDetailSerializer should return a serialized version of a bootcamp application
    with related data
    """
    application = app_data.application
    if not has_resume:
        application.resume_file = None
        application.save()

    data = BootcampApplicationDetailSerializer(instance=application).data
    assert data == {
        "id": application.id,
        "bootcamp_run": BootcampRunSerializer(application.bootcamp_run).data,
        "state": application.state,
        "resume_filepath": application.resume_file.name if has_resume else None,
        "linkedin_url": application.linkedin_url,
        "resume_upload_date": serializer_date_format(application.resume_upload_date),
        "payment_deadline": serializer_date_format(app_data.installment.deadline),
        "created_on": serializer_date_format(application.created_on),
        "is_paid_in_full": True,
        "run_application_steps": BootcampRunStepSerializer(
            instance=app_data.run_steps, many=True
        ).data,
        "submissions": [],
        "orders": [],
        "price": application.price,
    }


def test_app_detail_serializer_deadline(app_data):
    """
    BootcampApplicationDetailSerializer results should include a payment deadline based on the
    bootcamp run installments
    """
    application = app_data.application
    later_installment = InstallmentFactory.create(
        bootcamp_run=application.bootcamp_run,
        deadline=(app_data.installment.deadline + timedelta(days=1)),
    )
    data = BootcampApplicationDetailSerializer(instance=application).data
    assert data["payment_deadline"] == serializer_date_format(
        later_installment.deadline
    )


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
@pytest.mark.parametrize("has_interview", [True, False])
def test_submission_review_serializer(has_interview):
    """Test SubmissionReviewSerializer"""
    user = UserFactory.create()
    run_step = BootcampRunApplicationStepFactory.create()
    submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application__user=user,
        run_application_step=run_step,
        bootcamp_application__bootcamp_run=run_step.bootcamp_run,
    )
    interview = InterviewFactory.create()
    if has_interview:
        interview_submission = VideoInterviewSubmissionFactory(interview=interview)
        submission.content_object = interview_submission
        submission.save()
    data = SubmissionReviewSerializer(instance=submission).data
    assert data == {
        "id": submission.id,
        "run_application_step_id": run_step.id,
        "submitted_date": serializer_date_format(submission.submitted_date),
        "review_status": submission.review_status,
        "review_status_date": serializer_date_format(submission.review_status_date),
        "learner": UserSerializer(instance=user).data,
        "interview_url": (interview.results_url if has_interview else None),
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
        (
            REVIEW_STATUS_WAITLISTED,
            False,
            False,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ),
        (
            REVIEW_STATUS_WAITLISTED,
            True,
            True,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ),
        (
            REVIEW_STATUS_WAITLISTED,
            False,
            True,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ),
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
    assert serializer.is_valid() is True

    serializer.save()

    bootcamp_application.refresh_from_db()
    submission.refresh_from_db()

    assert submission.review_status == review
    assert bootcamp_application.state == expected


@pytest.mark.parametrize(
    "prior_status, new_status, prior_state, expected_state",
    [
        [
            REVIEW_STATUS_APPROVED,
            REVIEW_STATUS_REJECTED,
            AppStates.AWAITING_PAYMENT.value,
            AppStates.REJECTED.value,
        ],
        [
            REVIEW_STATUS_APPROVED,
            REVIEW_STATUS_REJECTED,
            AppStates.AWAITING_USER_SUBMISSIONS.value,
            AppStates.REJECTED.value,
        ],
        [
            REVIEW_STATUS_APPROVED,
            REVIEW_STATUS_WAITLISTED,
            AppStates.AWAITING_PAYMENT.value,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ],
        [
            REVIEW_STATUS_REJECTED,
            REVIEW_STATUS_APPROVED,
            AppStates.REJECTED.value,
            AppStates.AWAITING_PAYMENT.value,
        ],
        [
            REVIEW_STATUS_REJECTED,
            REVIEW_STATUS_WAITLISTED,
            AppStates.REJECTED.value,
            AppStates.AWAITING_SUBMISSION_REVIEW.value,
        ],
    ],
)
def test_submission_review_serializer_reverse_decision(
    prior_status, new_status, prior_state, expected_state
):
    """Test that submission decisions can be reversed"""
    bootcamp_application = BootcampApplicationFactory.create(state=prior_state)
    submission = ApplicationStepSubmissionFactory.create(
        review_status=prior_status,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
    )

    serializer = SubmissionReviewSerializer(submission, {"review_status": new_status})
    assert serializer.is_valid() is True

    serializer.save()

    bootcamp_application.refresh_from_db()
    submission.refresh_from_db()

    assert submission.review_status == new_status
    assert bootcamp_application.state == expected_state


@pytest.mark.parametrize(
    "app_state,total_paid",
    [
        [AppStates.AWAITING_RESUME, 0],
        [AppStates.COMPLETE, 0],
        [AppStates.AWAITING_PROFILE_COMPLETION, 0],
        [AppStates.AWAITING_SUBMISSION_REVIEW, 40],
    ],
)
def test_submission_review_serializer_validation(app_state, total_paid):
    """Test that status changes are invalidated if the application state is incorrect"""
    bootcamp_application = BootcampApplicationFactory.create(state=app_state)
    if total_paid > 0:
        OrderFactory.create(
            application=bootcamp_application, total_price_paid=total_paid
        )

    submission = ApplicationStepSubmissionFactory.create(
        review_status=REVIEW_STATUS_PENDING,
        bootcamp_application=bootcamp_application,
        run_application_step__bootcamp_run=bootcamp_application.bootcamp_run,
    )
    serializer = SubmissionReviewSerializer(
        submission, {"review_status": REVIEW_STATUS_APPROVED}
    )
    with pytest.raises(InvalidApplicationStateException) as ex:
        serializer.is_valid()
    assert ex.value.detail == "Bootcamp application is in invalid state"
