"""Applications models tests"""
from functools import reduce
from operator import or_

from django.db import models

from applications.constants import SubmissionTypes
from applications.models import (
    ApplicationStepSubmission,
    APP_SUBMISSION_MODELS,
)


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
