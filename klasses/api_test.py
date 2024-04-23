"""
klasses API tests
"""

# pylint: disable=redefined-outer-name
import datetime
from datetime import timedelta
from types import SimpleNamespace

import factory
import pytest
import pytz
from django.core.exceptions import ValidationError
from django.db.models import signals
from mitol.common.utils import now_in_utc

from applications.constants import AppStates
from applications.factories import BootcampApplicationFactory
from applications.models import BootcampApplication
from ecommerce.factories import LineFactory, OrderFactory
from ecommerce.models import Order
from klasses.api import (
    adjust_app_state_for_new_price,
    create_run_enrollment,
    create_run_enrollments,
    deactivate_run_enrollment,
    defer_enrollment,
    fetch_bootcamp_run,
)
from klasses.constants import (
    ENROLL_CHANGE_STATUS_DEFERRED,
    ENROLL_CHANGE_STATUS_REFUNDED,
)
from klasses.factories import (
    BootcampFactory,
    BootcampRunEnrollmentFactory,
    BootcampRunFactory,
    InstallmentFactory,
    PersonalPriceFactory,
)
from klasses.models import BootcampRun, BootcampRunEnrollment
from main import features

RUN_PRICE = 1000


@pytest.fixture(autouse=True)
def default_settings(settings):
    """
    Default settings fixture for API tests
    """
    settings.FEATURES[features.NOVOED_INTEGRATION] = False


@pytest.fixture()
def patched_create_run_enrollment(mocker):
    """patched create_run_enrollment"""
    return mocker.patch("klasses.api.create_run_enrollment", return_value=None)


@pytest.fixture()
def patched_deactivate_run_enrollment(mocker):
    """patched deactivate_run_enrollment"""
    return mocker.patch("klasses.api.deactivate_run_enrollment", return_value=[])


@pytest.fixture()
def enrollment_data(user):
    """enrollment data for testing"""
    bootcamps = BootcampFactory.create_batch(2)
    enrollments = BootcampRunEnrollmentFactory.create_batch(
        3,
        user=user,
        active=factory.Iterator([False, True, True]),
        bootcamp_run__bootcamp=factory.Iterator(
            [bootcamps[0], bootcamps[0], bootcamps[1]]
        ),
    )
    unenrollable_run = BootcampRunFactory.create(
        end_date=now_in_utc() - timedelta(days=1)
    )
    order = OrderFactory.create(user=user)
    return SimpleNamespace(
        bootcamps=bootcamps,
        enrollments=enrollments,
        unenrollable_run=unenrollable_run,
        order=order,
    )


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
    settings.FEATURES[features.NOVOED_INTEGRATION] = True
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
        2,
        order__user=user,
        order__status=Order.FULFILLED,
        bootcamp_run=run,
        price=int(RUN_PRICE / 2),
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
@pytest.mark.parametrize("order_status", [Order.CREATED, Order.FULFILLED])
def test_adjust_app_state_for_new_price_with_existing_orders(order_status):
    """
    Test that adjust_app_state_for_new_price updates an application when personal price exists
    and partial payment is made with an order in fulfilled status.
    """
    app = BootcampApplicationFactory.create(state=AppStates.AWAITING_PAYMENT.value)
    run = app.bootcamp_run
    user = app.user
    personal_price = PersonalPriceFactory.create(price=990, user=user, bootcamp_run=run)
    InstallmentFactory.create(bootcamp_run=run, amount=RUN_PRICE)
    # Create payments to test fulfilled and pending payments
    LineFactory.create_batch(
        2,
        order__user=user,
        order__status=order_status,
        bootcamp_run=run,
        price=int(RUN_PRICE / 2),
    )
    returned_app = adjust_app_state_for_new_price(
        user=user, bootcamp_run=run, new_price=getattr(personal_price, "price", None)
    )
    if order_status == Order.CREATED:
        assert returned_app is None
    else:
        app.refresh_from_db()
        assert isinstance(returned_app, BootcampApplication)
        assert returned_app.id == app.id
        assert app.state == AppStates.COMPLETE.value


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


def test_create_run_enrollments(mocker, patched_create_run_enrollment, user):
    """test create_run_enrollments"""
    bootcamp = BootcampFactory.create()
    bootcamp_runs = BootcampRunFactory.create_batch(3, bootcamp=bootcamp)
    create_run_enrollments(user, bootcamp_runs)
    assert patched_create_run_enrollment.call_count == 3
    expected_calls = []
    for run in bootcamp_runs:
        expected_calls.append(mocker.call(user, run, None))
    patched_create_run_enrollment.assert_has_calls(expected_calls)


@pytest.mark.django_db
@pytest.mark.parametrize("novoed_integration", [True, False])
def test_create_run_enrollment(mocker, user, settings, novoed_integration):
    """
    create_run_enrollment should call the novoed API to create enrollments, create or reactivate local
    enrollment records
    """
    settings.FEATURES[features.NOVOED_INTEGRATION] = novoed_integration

    num_runs = 3
    order = OrderFactory.create()
    runs = BootcampRunFactory.create_batch(num_runs)
    BootcampRunEnrollmentFactory.create(
        user=user,
        bootcamp_run=runs[0],
        change_status=ENROLL_CHANGE_STATUS_REFUNDED,
        active=False,
    )
    patched_novoed_enroll = mocker.patch(
        "klasses.api.novoed_tasks.enroll_users_in_novoed_course.delay"
    )

    assert user.profile.can_skip_application_steps is False
    successful_enrollments = []
    for run in runs:
        successful_enrollments.append(create_run_enrollment(user, run, order=order))
    if novoed_integration:
        assert patched_novoed_enroll.call_count == 3

        expected_calls = []
        for run in runs:
            expected_calls.append(
                mocker.call(
                    novoed_course_stub=run.novoed_course_stub, user_ids=[user.id]
                )
            )
        patched_novoed_enroll.assert_has_calls(expected_calls)

    assert len(successful_enrollments) == num_runs
    assert user.profile.can_skip_application_steps is True
    enrollments = BootcampRunEnrollment.objects.order_by("bootcamp_run__id").all()
    for run, enrollment in zip(runs, enrollments):
        assert enrollment.change_status is None
        assert enrollment.active is True
        assert enrollment.bootcamp_run == run


@pytest.mark.django_db
def test_create_run_enrollments_creation_fail(caplog, mocker, user):
    """
    create_run_enrollments should log a message and send an admin email if there's an error during the
    creation of local enrollment records
    """
    run = BootcampRunFactory()
    mocker.patch(
        "klasses.api.BootcampRunEnrollment.objects.get_or_create",
        side_effect=[Exception()],
    )
    patched_novoed_enroll = mocker.patch(
        "klasses.api.novoed_tasks.enroll_users_in_novoed_course.delay"
    )

    with pytest.raises(Exception):
        successful_enrollments = create_run_enrollments(user, [run], order=None)
        patched_novoed_enroll.assert_not_called()
        assert successful_enrollments == []
        assert (
            f"Failed to create/update enrollment record (user: user_{user.id}, run: {run.bootcamp_run_id}, order: {None})"
            in caplog.text
        )


@pytest.mark.parametrize("force", [True, False])
@pytest.mark.django_db
def test_defer_enrollment(mocker, user, force):
    """
    defer_enrollment should deactivate a user's existing enrollment and create an enrollment in another
    bootcamp run
    """
    bootcamp = BootcampFactory.create()
    bootcamp_runs = BootcampRunFactory.create_batch(3, bootcamp=bootcamp)
    order = OrderFactory.create(user=user, application__bootcamp_run=bootcamp_runs[0])
    existing_enrollment = BootcampRunEnrollmentFactory.create(
        bootcamp_run=bootcamp_runs[0], user=user
    )
    target_run = bootcamp_runs[1]
    mock_new_enrollment = mocker.Mock()
    patched_create_enrollment = mocker.patch(
        "klasses.api.create_run_enrollment",
        autospec=True,
        return_value=mock_new_enrollment if force else None,
    )
    patched_deactivate_enrollments = mocker.patch(
        "klasses.api.deactivate_run_enrollment",
        autospec=True,
        return_value=existing_enrollment if force else None,
    )

    returned_from_enrollment, returned_to_enrollment = defer_enrollment(
        existing_enrollment.user,
        existing_enrollment.bootcamp_run.bootcamp_run_id,
        bootcamp_runs[1].bootcamp_run_id,
        order.id,
        force=force,
    )
    assert returned_from_enrollment == patched_deactivate_enrollments.return_value
    assert returned_to_enrollment == patched_create_enrollment.return_value
    patched_create_enrollment.assert_called_once_with(
        existing_enrollment.user, target_run, order=order
    )
    assert patched_deactivate_enrollments.call_count == 1
    assert patched_deactivate_enrollments.call_args == mocker.call(
        change_status=ENROLL_CHANGE_STATUS_DEFERRED, run_enrollment=existing_enrollment
    )


@pytest.mark.django_db
def test_defer_enrollment_expired_enrollment_period_validation(
    enrollment_data,
    patched_create_run_enrollment,
    patched_deactivate_run_enrollment,
    user,
):
    """
    defer_enrollment should raise an exception if to bootcamp_run that is outside of its enrollment period
    """
    with pytest.raises(ValidationError):
        # Deferring to a bootcamp run that is outside of its enrollment period should raise a validation error
        defer_enrollment(
            user,
            enrollment_data.enrollments[0].bootcamp_run.bootcamp_run_id,
            enrollment_data.unenrollable_run.bootcamp_run_id,
            enrollment_data.order.id,
        )
    patched_create_run_enrollment.assert_not_called()


@pytest.mark.django_db
def test_defer_enrollment_different_bootcamp_validation(
    enrollment_data,
    patched_create_run_enrollment,
    patched_deactivate_run_enrollment,
    user,
):
    """
    defer_enrollment should raise an exception if to belongs to a different bootcamp
    """
    with pytest.raises(ValidationError):
        # Deferring to a bootcamp run in a different bootcamp should raise a validation error
        defer_enrollment(
            user,
            enrollment_data.enrollments[1].bootcamp_run.bootcamp_run_id,
            enrollment_data.enrollments[2].bootcamp_run.bootcamp_run_id,
            enrollment_data.order.id,
        )
    patched_create_run_enrollment.assert_not_called()


@pytest.mark.django_db
def test_defer_enrollment_inactive_enrollment_validation(
    enrollment_data,
    patched_create_run_enrollment,
    patched_deactivate_run_enrollment,
    user,
):
    """
    defer_enrollment from an inactive enrollment
    """
    with pytest.raises(ValidationError):
        # Deferring from an inactive enrollment should raise a validation error
        defer_enrollment(
            user,
            enrollment_data.enrollments[0].bootcamp_run.bootcamp_run_id,
            enrollment_data.enrollments[1].bootcamp_run.bootcamp_run_id,
            enrollment_data.order.id,
        )
    patched_create_run_enrollment.assert_not_called()


@pytest.mark.django_db
def test_defer_enrollment_invalid_order_validation(
    enrollment_data,
    patched_create_run_enrollment,
    patched_deactivate_run_enrollment,
    user,
):
    """
    defer_enrollment from an invalid order
    """
    with pytest.raises(ValidationError):
        # Deferring to a bootcamp run in a different bootcamp should raise a validation error for invalid order
        defer_enrollment(
            user,
            enrollment_data.enrollments[1].bootcamp_run.bootcamp_run_id,
            enrollment_data.enrollments[2].bootcamp_run.bootcamp_run_id,
            100,
        )
    patched_create_run_enrollment.assert_not_called()


@pytest.mark.django_db
def test_defer_enrollment_forced_validation(
    enrollment_data,
    patched_create_run_enrollment,
    patched_deactivate_run_enrollment,
    user,
):
    """
    defer_enrollment should not raise an exception if used force
    """
    # The last two cases should not raise an exception if the 'force' flag is set to True
    defer_enrollment(
        user,
        enrollment_data.enrollments[0].bootcamp_run.bootcamp_run_id,
        enrollment_data.enrollments[1].bootcamp_run.bootcamp_run_id,
        enrollment_data.order.id,
        force=True,
    )
    assert patched_create_run_enrollment.call_count == 1
    defer_enrollment(
        user,
        enrollment_data.enrollments[1].bootcamp_run.bootcamp_run_id,
        enrollment_data.enrollments[2].bootcamp_run.bootcamp_run_id,
        enrollment_data.order.id,
        force=True,
    )
    assert patched_create_run_enrollment.call_count == 2
