"""Tests for application interview state reset management command"""

import pytest
from django.core.management.base import CommandError

from applications.constants import REVIEWABLE_APP_STATES, AppStates
from applications.factories import BootcampApplicationFactory
from applications.management.commands import reset_application_interview_state

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "state",
    set(item.value for item in AppStates).difference(set(REVIEWABLE_APP_STATES)),  # noqa: C401
)
def test_reset_application_interview_state_prints_error_on_invalid_states(state):
    """Test that the reset interview command throws an error when the application is in Approved state already"""
    user_application = BootcampApplicationFactory.create(state=state)
    with pytest.raises(CommandError) as command_error:
        reset_application_interview_state.Command().handle(
            user=user_application.user.username,
            run=str(user_application.bootcamp_run.id),
        )
    assert (
        str(command_error.value)
        == f"User's application is not in a reviewable state. User={user_application.user}, Run={user_application.bootcamp_run}, "
        f"State={user_application.state}."
    )


@pytest.mark.parametrize(
    "state",
    REVIEWABLE_APP_STATES,
)
def test_reset_application_interview_state_success(state):
    """Test that the reset interview command throws an error when the application is in Approved state already"""
    user_application = BootcampApplicationFactory.create(state=state)

    reset_application_interview_state.Command().handle(
        user=user_application.user.username, run=str(user_application.bootcamp_run.id)
    )

    user_application.refresh_from_db()
    assert user_application.state == AppStates.AWAITING_USER_SUBMISSIONS.value
