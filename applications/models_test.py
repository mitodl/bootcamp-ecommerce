"""Applications models tests"""
from functools import reduce
from operator import or_
import pytest

from django.core.exceptions import ValidationError
from django.db import models

from applications.constants import SubmissionTypes
from applications.models import (
    ApplicationStepSubmission,
    APP_SUBMISSION_MODELS,
)
from applications.factories import BootcampRunApplicationStepFactory, ApplicationStepSubmissionFactory
from klasses.factories import BootcampFactory, BootcampRunFactory


def test_submission_types():
    """
    The enum of valid submission types should match the list of models that are defined as valid submission types,
    and the choices for the submissions' content type should be limited to that list of models
    """
    assert len(SubmissionTypes) == len(APP_SUBMISSION_MODELS)
    assert {model_cls.submission_type for model_cls in APP_SUBMISSION_MODELS} == {
        sub_type.value for sub_type in SubmissionTypes
    }
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
