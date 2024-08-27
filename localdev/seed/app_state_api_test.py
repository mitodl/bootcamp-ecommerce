"""Tests for API functionality that sets the state of an application"""

import pytest

from applications.api import derive_application_state
from applications.constants import ORDERED_UNFINISHED_APP_STATES, AppStates
from applications.factories import (
    BootcampApplicationFactory,
    BootcampRunApplicationStepFactory,
)
from klasses.factories import BootcampRunFactory, InstallmentFactory
from localdev.seed.app_state_api import (
    ORDERED_APPLICATION_STEP_CLASSES,
    set_application_state,
)


@pytest.fixture
def app_bootcamp_run():
    """Fixture for a bootcamp run with application steps and a non-zero price"""
    run = BootcampRunFactory.create()
    BootcampRunApplicationStepFactory.create_batch(2, bootcamp_run=run)
    InstallmentFactory.create(bootcamp_run=run, amount=100)
    return run


def test_app_state_classes():
    """
    There should be an app state class defined for each of the possible unfinished application states, and they
    should be in the correct order
    """
    assert [
        app_step_cls.state for app_step_cls in ORDERED_APPLICATION_STEP_CLASSES
    ] == ORDERED_UNFINISHED_APP_STATES


@pytest.mark.django_db
@pytest.mark.parametrize(
    "target_state",
    [
        AppStates.AWAITING_PROFILE_COMPLETION.value,
        AppStates.AWAITING_RESUME.value,
        AppStates.AWAITING_USER_SUBMISSIONS.value,
        AppStates.AWAITING_SUBMISSION_REVIEW.value,
        AppStates.AWAITING_PAYMENT.value,
        AppStates.COMPLETE.value,
    ],
)
def test_set_application_state(app_bootcamp_run, target_state):
    """set_application_state should manipulate a bootcamp application into a certain state"""
    bootcamp_app = BootcampApplicationFactory.create(bootcamp_run=app_bootcamp_run)
    bootcamp_app = set_application_state(bootcamp_app, target_state)
    assert bootcamp_app.state == target_state
    assert derive_application_state(bootcamp_app) == target_state


@pytest.mark.django_db
@pytest.mark.parametrize(
    "target_state",
    [
        AppStates.AWAITING_PROFILE_COMPLETION.value,
        AppStates.AWAITING_RESUME.value,
        AppStates.AWAITING_USER_SUBMISSIONS.value,
        AppStates.AWAITING_SUBMISSION_REVIEW.value,
        AppStates.AWAITING_PAYMENT.value,
    ],
)
def test_set_application_state_revert(app_bootcamp_run, target_state):
    """set_application_state should be able to roll a bootcamp application back to a previous state"""
    bootcamp_app = BootcampApplicationFactory.create(bootcamp_run=app_bootcamp_run)
    # First set the bootcamp application to be completed
    bootcamp_app = set_application_state(bootcamp_app, AppStates.COMPLETE.value)
    # Then set to the target state
    bootcamp_app = set_application_state(bootcamp_app, target_state)
    assert bootcamp_app.state == target_state
    assert derive_application_state(bootcamp_app) == target_state
