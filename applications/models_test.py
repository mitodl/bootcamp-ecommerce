"""Applications models tests"""
from functools import reduce
from operator import or_, itemgetter
import pytest

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models


from applications.constants import VALID_SUBMISSION_TYPE_CHOICES, REVIEW_STATUS_APPROVED, REVIEW_STATUS_REJECTED
from applications.models import (
    ApplicationStepSubmission,
    APP_SUBMISSION_MODELS,
)
from applications.factories import BootcampRunApplicationStepFactory, ApplicationStepSubmissionFactory, \
    BootcampApplicationFactory
from applications.constants import AppStates
from klasses.factories import BootcampFactory, BootcampRunFactory


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
        )  # pylint: disable=protected-access
    )
    assert (
        ApplicationStepSubmission._meta.get_field("content_type").get_limit_choices_to() == expected_content_type_limit
    )  # pylint: disable=protected-access


@pytest.mark.django_db
@pytest.mark.parametrize("file_name,expected", [
    ('resume.pdf', True),
    ('resume', False),
    ('resume.doc', True),
    ('resume.docx', True),
    ('resume.png', False)
])
def test_bootcamp_application_resume_file_validation(file_name, expected):
    """
    A BootcampApplication should raise an exception if profile is not complete or extension is not allowed
    """
    bootcamp_application = BootcampApplicationFactory(state=AppStates.AWAITING_RESUME.value)
    resume_file = SimpleUploadedFile(file_name, b'file_content')

    if expected:
        bootcamp_application.upload_resume(resume_file)
        assert bootcamp_application.state == AppStates.AWAITING_USER_SUBMISSIONS.value
    else:
        with pytest.raises(ValidationError):
            bootcamp_application.upload_resume(resume_file)
        assert bootcamp_application.state == AppStates.AWAITING_RESUME.value


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
        review_status=REVIEW_STATUS_APPROVED
    )
    bootcamp_application = submission.bootcamp_application

    assert bootcamp_application.is_ready_for_payment() is True

    application_step = BootcampRunApplicationStepFactory.create(
        bootcamp_run=bootcamp_run,
        application_step__bootcamp=bootcamp_run.bootcamp
    )
    submission_not_approved = ApplicationStepSubmissionFactory.create(
        review_status=None,
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
        application_step__bootcamp=bootcamps[0],
        bootcamp_run__bootcamp=bootcamps[0],
    )
    step.bootcamp_run.bootcamp = bootcamps[1]
    with pytest.raises(ValidationError):
        step.save()
    step.bootcamp_run.bootcamp = bootcamps[0]
    step.save()


@pytest.mark.django_db
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
