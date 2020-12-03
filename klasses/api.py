"""
API functionality for bootcamps
"""
from datetime import datetime, timedelta

import pytz

from klasses.constants import DATE_RANGE_MONTH_FMT
from klasses.models import BootcampRun


def deactivate_run_enrollment(run_enrollment, change_status):
    """
    Helper method to deactivate a BootcampRunEnrollment

    Args:
        run_enrollment (BootcampRunEnrollment): The bootcamp run enrollment to deactivate
        change_status (str): The change status to set on the enrollment when deactivating

    Returns:
        BootcampRunEnrollment: The updated enrollment
    """
    run_enrollment.active = False
    run_enrollment.change_status = change_status
    run_enrollment.save()


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
