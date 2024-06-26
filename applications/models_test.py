"""Applications models tests"""

from functools import reduce
from operator import or_, itemgetter
from unittest.mock import PropertyMock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
import pytest
from django_fsm import TransitionNotAllowed

from applications.constants import (
    VALID_SUBMISSION_TYPE_CHOICES,
    REVIEW_STATUS_REJECTED,
    LETTER_TYPE_REJECTED,
    LETTER_TYPE_APPROVED,
)
from applications.models import ApplicationStepSubmission, APP_SUBMISSION_MODELS
from applications.factories import (
    BootcampRunApplicationStepFactory,
    ApplicationStepSubmissionFactory,
    BootcampApplicationFactory,
    ApplicationStepFactory,
)
from applications.constants import AppStates
from ecommerce.test_utils import create_test_application, create_test_order
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.factories import (
    BootcampFactory,
    BootcampRunFactory,
    InstallmentFactory,
    PersonalPriceFactory,
)
from klasses.models import Installment, PersonalPrice, BootcampRunEnrollment

# pylint: disable=redefined-outer-name,unused-argument
from main.features import NOVOED_INTEGRATION

pytestmark = pytest.mark.django_db


@pytest.fixture
def application():
    """An application for testing"""
    yield create_test_application()


@pytest.fixture
def user(application):
    """A user with social auth"""
    yield application.user


@pytest.fixture
def bootcamp_run(application):
    """
    Creates a purchasable bootcamp run. Bootcamp run price is at least $200, in two installments
    """
    yield application.bootcamp_run


@pytest.fixture()
def patched_novoed_tasks(mocker):
    """Patched novoed-related tasks"""
    return mocker.patch("klasses.api.novoed_tasks")


PAYMENT = 123


def test_submission_types():
    """
    The list of valid submission types should match the list of models that are defined as valid submission types,
    and the choices for the submissions' content type should be limited to that list of models
    """
    assert len(APP_SUBMISSION_MODELS) == len(VALID_SUBMISSION_TYPE_CHOICES)
    # The choices for ApplicationStep.submission_type should match the models
    # that we have defined as valid submission models
    assert {model_cls._meta.model_name for model_cls in APP_SUBMISSION_MODELS} == set(
        map(itemgetter(0), VALID_SUBMISSION_TYPE_CHOICES)
    )

    # Build an OR query with every valid submission model
    expected_content_type_limit = reduce(
        or_,
        (
            models.Q(app_label="applications", model=model_cls._meta.model_name)
            for model_cls in APP_SUBMISSION_MODELS
        ),  # pylint: disable=protected-access
    )
    assert (
        ApplicationStepSubmission._meta.get_field("content_type").get_limit_choices_to()
        == expected_content_type_limit
    )  # pylint: disable=protected-access


def test_bootcamp_application_with_no_steps_file_submission():
    """
    A bootcamp application with no steps
    """
    bootcamp_application = BootcampApplicationFactory(
        state=AppStates.AWAITING_RESUME.value
    )
    resume_file = SimpleUploadedFile("resume.pdf", b"file_content")
    bootcamp_application.add_resume(resume_file=resume_file)
    assert bootcamp_application.state == AppStates.AWAITING_PAYMENT.value


@pytest.mark.parametrize(
    "file_name,state,expected",
    [
        ("resume.pdf", AppStates.AWAITING_RESUME.value, True),
        ("resume.pdf", AppStates.AWAITING_SUBMISSION_REVIEW.value, True),
        ("resume.pdf", AppStates.AWAITING_USER_SUBMISSIONS.value, True),
        ("resume.pdf", AppStates.AWAITING_PAYMENT.value, False),
        ("resume", AppStates.AWAITING_RESUME.value, False),
        ("resume.doc", AppStates.AWAITING_RESUME.value, True),
        ("resume.docx", AppStates.AWAITING_SUBMISSION_REVIEW.value, True),
        ("resume.png", AppStates.AWAITING_RESUME.value, False),
    ],
)
def test_bootcamp_application_resume_file_validation(file_name, state, expected):
    """
    A BootcampApplication should raise an exception if profile is not complete or extension is not allowed
    """
    bootcamp_application = BootcampApplicationFactory(state=state)
    resume_file = SimpleUploadedFile(file_name, b"file_content")

    application_step = ApplicationStepFactory(
        bootcamp=bootcamp_application.bootcamp_run.bootcamp
    )
    BootcampRunApplicationStepFactory(
        bootcamp_run=bootcamp_application.bootcamp_run,
        application_step=application_step,
    )

    if expected:
        new_state = (
            AppStates.AWAITING_USER_SUBMISSIONS.value
            if state == AppStates.AWAITING_RESUME.value
            else state
        )
        bootcamp_application.add_resume(resume_file=resume_file)
        assert bootcamp_application.state == new_state
    else:
        with pytest.raises((ValidationError, TransitionNotAllowed)):
            bootcamp_application.add_resume(resume_file=resume_file)
        assert bootcamp_application.state == state


def test_bootcamp_application_complete(settings, patched_novoed_tasks):
    """
    BootcampApplication.complete should create an enrollment and call a task to enroll the user in the course on
    NovoEd
    """
    settings.FEATURES[NOVOED_INTEGRATION] = True
    novoed_course_stub = "course-stub"
    bootcamp_application = BootcampApplicationFactory.create(
        state=AppStates.AWAITING_PAYMENT.value,
        bootcamp_run__novoed_course_stub=novoed_course_stub,
    )
    assert not bootcamp_application.user.profile.can_skip_application_steps
    bootcamp_application.complete()
    assert BootcampRunEnrollment.objects.filter(
        user=bootcamp_application.user,
        bootcamp_run=bootcamp_application.bootcamp_run,
        active=True,
    ).exists()
    assert bootcamp_application.user.profile.can_skip_application_steps
    patched_novoed_tasks.enroll_users_in_novoed_course.delay.assert_called_once_with(
        user_ids=[bootcamp_application.user.id], novoed_course_stub=novoed_course_stub
    )


@pytest.mark.django_db
def test_application_await_further_payment(mocker):
    """
    BootcampApplication.await_further_payment should call an API function to deactivate an enrollment
    """
    patched_deactivate = mocker.patch("applications.models.deactivate_run_enrollment")
    bootcamp_application = BootcampApplicationFactory(state=AppStates.COMPLETE.value)
    bootcamp_application.await_further_payment()
    patched_deactivate.assert_called_once_with(
        user=bootcamp_application.user,
        bootcamp_run=bootcamp_application.bootcamp_run,
        change_status=None,
    )


@pytest.mark.django_db
def test_application_refund(mocker):
    """
    BootcampApplication.refund should call an API function to deactivate an enrollment
    """
    patched_deactivate = mocker.patch("applications.models.deactivate_run_enrollment")
    bootcamp_application = BootcampApplicationFactory(state=AppStates.COMPLETE.value)
    bootcamp_application.refund()
    patched_deactivate.assert_called_once_with(
        user=bootcamp_application.user,
        bootcamp_run=bootcamp_application.bootcamp_run,
        change_status=ENROLL_CHANGE_STATUS_REFUNDED,
    )


@pytest.mark.django_db
def test_is_ready_for_payment():
    """
    is_ready_for_payment should return true if all application steps are submitted
    and reviewed
    """
    bootcamp_run = BootcampRunFactory()
    submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application__bootcamp_run=bootcamp_run,
        run_application_step__bootcamp_run=bootcamp_run,
        is_approved=True,
    )
    bootcamp_application = submission.bootcamp_application

    assert bootcamp_application.is_ready_for_payment() is True

    application_step = BootcampRunApplicationStepFactory.create(
        bootcamp_run=bootcamp_run, application_step__bootcamp=bootcamp_run.bootcamp
    )
    submission_not_approved = ApplicationStepSubmissionFactory.create(
        is_pending=True,
        bootcamp_application=bootcamp_application,
        run_application_step=application_step,
    )
    assert bootcamp_application.is_ready_for_payment() is False

    submission_not_approved.review_status = REVIEW_STATUS_REJECTED
    submission_not_approved.save()

    assert bootcamp_application.is_ready_for_payment() is False


@pytest.mark.django_db
def test_bootcamp_run_application_step_validation():
    """
    A BootcampRunApplicationStep object should raise an exception if it is saved when the bootcamp of the bootcamp run
    and step are not the same.
    """
    bootcamps = BootcampFactory.create_batch(2)
    step = BootcampRunApplicationStepFactory.create(
        application_step__bootcamp=bootcamps[0], bootcamp_run__bootcamp=bootcamps[0]
    )
    step.bootcamp_run.bootcamp = bootcamps[1]
    with pytest.raises(ValidationError):
        step.save()
    step.bootcamp_run.bootcamp = bootcamps[0]
    step.save()


def test_app_step_submission_validation():
    """
    An ApplicationStepSubmission object should raise an exception if it is saved when the bootcamp run of the
    application and the step are not the same.
    """
    bootcamp_runs = BootcampRunFactory.create_batch(2)
    submission = ApplicationStepSubmissionFactory.create(
        bootcamp_application__bootcamp_run=bootcamp_runs[0],
        run_application_step__bootcamp_run=bootcamp_runs[0],
    )
    submission.bootcamp_application.bootcamp_run = bootcamp_runs[1]
    with pytest.raises(ValidationError):
        submission.save()
    submission.bootcamp_application.bootcamp_run = bootcamp_runs[0]
    submission.save()


def test_get_total_paid(application):
    """
    get_total_paid should look through all fulfilled orders for the payment for a particular user
    """
    # Multiple payments should be added together
    create_test_order(application, PAYMENT, fulfilled=True)
    next_payment = 50
    create_test_order(application, next_payment, fulfilled=True)
    assert application.total_paid == PAYMENT + next_payment


def test_get_total_paid_unfulfilled(application):
    """Unfulfilled orders should be ignored"""
    create_test_order(application, 45, fulfilled=False)
    assert application.total_paid == 0


def test_get_total_paid_other_run(application):
    """Orders for other bootcamp runs should be ignored"""
    other_application = create_test_application()
    create_test_order(other_application, 50, fulfilled=True)
    assert application.total_paid == 0


def test_get_total_paid_no_payments(application):
    """If there are no payments get_total_paid should return 0"""
    assert application.total_paid == 0


@pytest.mark.parametrize(
    "run_price,personal_price,expected_price",
    [[10, None, 10], [10, 5, 5], [10, 25, 25]],
)  # pylint: disable=too-many-arguments
def test_price(
    application, bootcamp_run, user, run_price, personal_price, expected_price
):
    """
    BootcampApplication.price should return the personal price for the run, or else the full price
    """
    Installment.objects.all().delete()
    for _ in range(2):
        InstallmentFactory.create(amount=run_price / 2, bootcamp_run=bootcamp_run)

    if personal_price is not None:
        # this price should be ignored
        PersonalPriceFactory.create(bootcamp_run=bootcamp_run)
        # this price should be used
        PersonalPrice.objects.create(
            bootcamp_run=bootcamp_run, user=user, price=personal_price
        )
        # this price should be ignored
        PersonalPriceFactory.create(bootcamp_run=bootcamp_run)

    assert application.price == expected_price


@pytest.mark.parametrize(
    "price,total_paid,expected_fully_paid",
    [[10, 10, True], [10, 9, False], [10, 11, True]],
)  # pylint: disable=too-many-arguments
def test_is_paid_in_full(mocker, application, price, total_paid, expected_fully_paid):
    """
    is_paid_in_full should return true if the payments match or exceed the price of the run
    """
    price_mock = mocker.patch(
        "applications.models.BootcampApplication.price", new_callable=PropertyMock
    )
    price_mock.return_value = price
    total_paid_mock = mocker.patch(
        "applications.models.BootcampApplication.total_paid", new_callable=PropertyMock
    )
    total_paid_mock.return_value = total_paid
    assert application.is_paid_in_full is expected_fully_paid


@pytest.mark.parametrize("ready_for_payment", [True, False])
def test_applicant_letter_approved(mocker, application, ready_for_payment):
    """If all submissions are approved, an applicant letter should be sent"""
    application.state = AppStates.AWAITING_SUBMISSION_REVIEW.value
    application.save()
    create_patched = mocker.patch(
        "applications.tasks.create_and_send_applicant_letter.delay"
    )
    ready_patched = mocker.patch(
        "applications.models.BootcampApplication.is_ready_for_payment",
        return_value=ready_for_payment,
    )
    application.approve_submission()
    ready_patched.assert_called_once_with()
    if ready_for_payment:
        create_patched.assert_called_once_with(
            application_id=application.id, letter_type=LETTER_TYPE_APPROVED
        )
    else:
        assert create_patched.called is False


def test_applicant_letter_rejected(mocker, application):
    """If any submission is rejected, an applicant letter should be sent"""
    application.state = AppStates.AWAITING_SUBMISSION_REVIEW.value
    application.save()
    create_patched = mocker.patch(
        "applications.tasks.create_and_send_applicant_letter.delay"
    )
    application.reject_submission()
    create_patched.assert_called_once_with(
        application_id=application.id, letter_type=LETTER_TYPE_REJECTED
    )
