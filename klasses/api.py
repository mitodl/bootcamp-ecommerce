"""
API functionality for bootcamps
"""
import logging
from datetime import datetime, timedelta

import pytz
from django.db.models import Sum

from applications.constants import AppStates
from ecommerce.models import Line
from klasses.constants import DATE_RANGE_MONTH_FMT
from klasses.models import BootcampRun, BootcampRunEnrollment
from main import features
from novoed import tasks as novoed_tasks


log = logging.getLogger(__name__)


def deactivate_run_enrollment(
    *, run_enrollment=None, user=None, bootcamp_run=None, change_status=None
):
    """
    Helper method to deactivate a BootcampRunEnrollment. Can accept a BootcampRunEnrollment as an argument, or a
    User and BootcampRun that can be used to find the enrollment.

    Args:
        run_enrollment (Optional[BootcampRunEnrollment]): The bootcamp run enrollment to deactivate
        user (Optional[User]): The enrolled user (only required if run_enrollment is not provided)
        bootcamp_run (Optional[BootcampRun]): The enrolled bootcamp run (only required if run_enrollment
            is not provided)
        change_status (Optional[str]): The change status to set on the enrollment when deactivating

    Returns:
        Optional[BootcampRunEnrollment]: The updated enrollment (or None if the enrollment doesn't exist)
    """
    if run_enrollment is None and (user is None or bootcamp_run is None):
        raise ValueError("Must provide run_enrollment, or both user and bootcamp_run")
    if run_enrollment is None:
        run_enrollment = BootcampRunEnrollment.objects.filter(
            user=user, bootcamp_run=bootcamp_run
        ).first()
        if run_enrollment is None:
            return
    run_enrollment.active = False
    run_enrollment.change_status = change_status
    run_enrollment.save()
    if (
        features.is_enabled(features.NOVOED_INTEGRATION)
        and run_enrollment.bootcamp_run.novoed_course_stub
    ):
        novoed_tasks.unenroll_user_from_novoed_course.delay(
            user_id=run_enrollment.user.id,
            novoed_course_stub=run_enrollment.bootcamp_run.novoed_course_stub,
        )
    return run_enrollment


def adjust_app_state_for_new_price(user, bootcamp_run, new_price=None):
    """
    Given a new price for a bootcamp run, updated user's bootcamp application if (a) it exists, and (b) the new price
    is such that the bootcamp application state is no longer valid (e.g.: the new price is greater than the
    amount that the user has paid, but the application is in the "complete" state)

    Args:
        user (User): The user whose application may be affected
        bootcamp_run (BootcampRun): The bootcamp run of the application that may be affected
        new_price (Optional[Any[int, Decimal]]): The new total price of the bootcamp run (if None, the bootcamp run's
            normal price will be used)

    Returns:
        Optional[BootcampApplication]: The bootcamp application for the user/run referred to by the personal price
            if it was modified (otherwise, None will be returned)
    """
    total_paid_qset = Line.objects.filter(
        order__user=user, bootcamp_run=bootcamp_run
    ).aggregate(aggregate_total_paid=Sum("price"))
    total_paid = total_paid_qset["aggregate_total_paid"] or 0
    new_price = new_price if new_price is not None else bootcamp_run.price
    needs_payment = total_paid < new_price
    application = user.bootcamp_applications.filter(
        bootcamp_run=bootcamp_run,
        # The state needs to change if (a) it's currently complete and now needs more payment, or (b) it's currently
        # awaiting payment and the new price means they don't need to pay any more.
        state=(
            AppStates.COMPLETE.value
            if needs_payment
            else AppStates.AWAITING_PAYMENT.value
        ),
    ).first()
    if application is None:
        return
    if needs_payment:
        application.await_further_payment()
    else:
        application.complete()
    application.save()
    log.info(
        "Personal price update caused application state change (user: %s, run: '%s', new state: %s)",
        user.email,
        bootcamp_run.title,
        application.state,
    )
    return application


def _parse_formatted_date_range(date_range_str):
    """
    Parses a string representing a date range (e.g.: "May 1, 2020 - Jan 30, 2021")

    Args:
        date_range_str (str): A string representing a date range

    Returns:
        Tuple[datetime.datetime, Optional[datetime.datetime]]: A tuple containing the two dates that were parsed from
            the string
    """
    if "-" not in date_range_str:
        date1_string = date_range_str
        date2_string = None
    else:
        date1_string, date2_string = date_range_str.split("-")
    date1_parts = date1_string.split(",")
    date1_monthday = date1_parts[0].strip().split(" ")
    month1, day1 = date1_monthday[0], int(date1_monthday[1])
    if not date2_string:
        year1 = int(date1_parts[1].strip())
        month2, day2, year2 = None, None, None
    else:
        date2_parts = date2_string.split(",")
        date2_monthday = date2_parts[0].strip().split(" ")
        year2 = int(date2_parts[1].strip())
        year1 = year2 if len(date1_parts) < 2 else int(date1_parts[1].strip())
        if len(date2_monthday) < 2:
            month2 = month1
            day2 = int(date2_monthday[0])
        else:
            month2 = date2_monthday[0]
            day2 = int(date2_monthday[1])
    date1 = datetime(
        year=year1,
        month=datetime.strptime(month1, DATE_RANGE_MONTH_FMT).month,
        day=day1,
        tzinfo=pytz.UTC,
    )
    date2 = (
        None
        if not date2_string
        else datetime(
            year=year2,
            month=datetime.strptime(month2, DATE_RANGE_MONTH_FMT).month,
            day=day2,
            tzinfo=pytz.UTC,
        )
    )
    return date1, date2


def fetch_bootcamp_run(run_property):
    """
    Fetches a bootcamp run that has a field value (id, title, etc.) that matches the given property

    Args:
        run_property (str): A string representing some field value for a specific bootcamp run

    Returns:
        BootcampRun: The bootcamp run matching the given property
    """
    if run_property.isdigit():
        return BootcampRun.objects.get(id=run_property)
    run = BootcampRun.objects.filter(title=run_property).first()
    if run is not None:
        return run
    # If run_property is a string and didn't match a title, it might be a 'display_title' property value.
    # Attempt to parse that and match it to a run.
    if run is None and "," not in run_property:
        return BootcampRun.objects.get(bootcamp__title=run_property)
    potential_bootcamp_title, potential_date_range = run_property.split(",", maxsplit=1)
    potential_start_date, potential_end_date = _parse_formatted_date_range(
        potential_date_range
    )
    run_filters = dict(bootcamp__title=potential_bootcamp_title)
    if potential_start_date:
        run_filters.update(
            dict(
                start_date__gte=potential_start_date,
                start_date__lt=potential_start_date + timedelta(days=1),
            )
        )
    else:
        run_filters["start_date"] = None
    if potential_end_date:
        run_filters.update(
            dict(
                end_date__gte=potential_end_date,
                end_date__lt=potential_end_date + timedelta(days=1),
            )
        )
    else:
        run_filters["end_date"] = None
    try:
        return BootcampRun.objects.get(**run_filters)
    except BootcampRun.DoesNotExist as exc:
        raise BootcampRun.DoesNotExist(
            "Could not find BootcampRun with the following filters: {}".format(
                run_filters
            )
        ) from exc
