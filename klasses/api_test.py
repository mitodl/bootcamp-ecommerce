"""
klasses API tests
"""
import datetime

import factory
import pytest
import pytz
from django.db.models import signals

from applications.constants import AppStates
from applications.factories import BootcampApplicationFactory
from applications.models import BootcampApplication
from ecommerce.factories import LineFactory
from klasses.api import (
    deactivate_run_enrollment,
    fetch_bootcamp_run,
    adjust_app_state_for_new_price,
)
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.factories import (
    BootcampRunFactory,
    BootcampRunEnrollmentFactory,
    PersonalPriceFactory,
    InstallmentFactory,
)
from klasses.models import BootcampRun
from main.features import NOVOED_INTEGRATION

RUN_PRICE = 1000


@pytest.fixture(autouse=True)
def default_settings(settings):
    """
    Default settings fixture for API tests
    """
    settings.FEATURES[NOVOED_INTEGRATION] = False


@pytest.mark.django_db
def test_deactivate_run_enrollment():
    """deactivate_run_enrollment should update enrollment fields correctly"""
    enrollments = BootcampRunEnrollmentFactory.create_batch(
        2, active=True, change_status=None
    )
    deactivate_run_enrollment(
        run_enrollment=enrollments[0], change_status=ENROLL_CHANGE_STATUS_REFUNDED
    )
    enrollments[0].refresh_from_db()
    assert enrollments[0].active is False
    assert enrollments[0].change_status == ENROLL_CHANGE_STATUS_REFUNDED
    deactivate_run_enrollment(
        user=enrollments[1].user,
        bootcamp_run=enrollments[1].bootcamp_run,
        change_status=None,
    )
    enrollments[1].refresh_from_db()
    assert enrollments[1].active is False
    assert enrollments[1].change_status is None


@pytest.mark.django_db
def test_deactivate_run_enrollment_novoed(mocker, settings):
    """deactivate_run_enrollment should run a task to unenroll users in NovoEd if the bootcamp run is NovoEd-enabled"""
    settings.FEATURES[NOVOED_INTEGRATION] = True
    patched_novoed_tasks = mocker.patch("klasses.api.novoed_tasks")
    novoed_stub = "novoed-course"
    enrollment = BootcampRunEnrollmentFactory.create(
        bootcamp_run__novoed_course_stub=novoed_stub
    )
    deactivate_run_enrollment(run_enrollment=enrollment, change_status=None)
    patched_novoed_tasks.unenroll_user_from_novoed_course.delay.assert_called_once_with(
        user_id=enrollment.user.id, novoed_course_stub=novoed_stub
    )


def test_deactivate_run_enrollment_bad_kwargs(mocker):
    """Test that deactivate_run_enrollment raises an exception if the wrong kwargs are provided"""
    with pytest.raises(ValueError):
        deactivate_run_enrollment(change_status=None)
    with pytest.raises(ValueError):
        deactivate_run_enrollment(user=mocker.Mock())
    with pytest.raises(ValueError):
        deactivate_run_enrollment(bootcamp_run=mocker.Mock())


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
@pytest.mark.parametrize(
    "personal_price_amt,init_state,expected_state",
    [
        [RUN_PRICE - 10, AppStates.AWAITING_PAYMENT.value, AppStates.COMPLETE.value],
        [RUN_PRICE + 10, AppStates.COMPLETE.value, AppStates.AWAITING_PAYMENT.value],
        [None, AppStates.AWAITING_PAYMENT.value, AppStates.COMPLETE.value],
    ],
)
def test_adjust_app_state_for_new_price(personal_price_amt, init_state, expected_state):
    """
    adjust_app_state_for_new_price should update a bootcamp application state if a personal price, compared with
    the amount the user has already paid, does not match with the current application state.
    """
    app = BootcampApplicationFactory.create(state=init_state)
    run = app.bootcamp_run
    user = app.user
    personal_price = (
        PersonalPriceFactory.create(
            price=personal_price_amt, user=user, bootcamp_run=run
        )
        if personal_price_amt
        else None
    )
    InstallmentFactory.create(bootcamp_run=run, amount=RUN_PRICE)
    # Create payments such that the user has paid the original bootcamp run price
    LineFactory.create_batch(
        2, order__user=user, bootcamp_run=run, price=int(RUN_PRICE / 2)
    )
    returned_app = adjust_app_state_for_new_price(
        user=user, bootcamp_run=run, new_price=getattr(personal_price, "price", None)
    )
    app.refresh_from_db()
    assert isinstance(returned_app, BootcampApplication)
    assert returned_app.id == app.id
    assert app.state == expected_state


@factory.django.mute_signals(signals.post_save)
@pytest.mark.django_db
def test_adjust_app_state_for_zero_price():
    """
    adjust_app_state_for_new_price should update a bootcamp application state to complete if the application was
    awaiting payment and the personal price was set to zero
    """
    app = BootcampApplicationFactory.create(state=AppStates.AWAITING_PAYMENT.value)
    InstallmentFactory.create(bootcamp_run=app.bootcamp_run, amount=10)
    returned_app = adjust_app_state_for_new_price(
        user=app.user, bootcamp_run=app.bootcamp_run, new_price=0
    )
    assert returned_app.state == AppStates.COMPLETE.value


@pytest.mark.django_db
def test_fetch_bootcamp_run():
    """fetch_bootcamp_run should fetch a bootcamp run with a field value that matches the given property"""
    run = BootcampRunFactory.create(
        bootcamp__title="Bootcamp 1", title="Run 1", start_date=None, end_date=None
    )
    assert fetch_bootcamp_run(str(run.id)) == run
    assert fetch_bootcamp_run(run.title) == run
    assert fetch_bootcamp_run(run.display_title) == run
    with pytest.raises(BootcampRun.DoesNotExist):
        fetch_bootcamp_run("invalid")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "end_date_params",
    [
        dict(year=2020, month=1, day=15),
        dict(year=2020, month=2, day=1),
        dict(year=2021, month=1, day=1),
        None,
    ],
)
def test_fetch_bootcamp_run_dates(end_date_params):
    """fetch_bootcamp_run should fetch a bootcamp run by display title regardless of the start/end date ranges"""
    run = BootcampRunFactory.create(
        bootcamp__title="Bootcamp 1",
        title="Run 1",
        start_date=datetime.datetime(year=2020, month=1, day=1, tzinfo=pytz.UTC),
        end_date=(
            None
            if not end_date_params
            else datetime.datetime(**end_date_params, tzinfo=pytz.UTC)
        ),
    )
    assert fetch_bootcamp_run(run.display_title) == run
    with pytest.raises(BootcampRun.DoesNotExist):
        fetch_bootcamp_run("invalid")
