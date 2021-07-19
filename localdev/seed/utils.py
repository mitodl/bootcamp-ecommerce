"""Seed data utility functions"""
import json
import re
from datetime import timedelta

from mitol.common.utils import now_in_utc

from localdev.seed.config import (
    SEED_DATA_FILE_PATH,
    SEED_DATA_PREFIX,
    SEED_DATA_KEY_FIELDS,
    DateRangeOption,
)


DEFAULT_RANGE_DAYS = 90
DEFAULT_OFFSET_DAYS = 60


class SeedDataSpec:  # pylint: disable=too-many-instance-attributes,too-many-arguments
    """Represents an object described by seed data and, if one is created/found, the actual database object"""

    def __init__(
        self,
        model_cls,
        index,
        raw_item_data,
        prev_sibling_data,
        next_sibling_data,
        child_object_data,
        parent_spec,
        db_object=None,
    ):
        self.model_cls = model_cls
        self.index = index
        self.raw_item_data = raw_item_data
        self.prev_sibling_data = prev_sibling_data
        self.next_sibling_data = next_sibling_data
        self.child_object_data = child_object_data
        self.parent_spec = parent_spec
        self.db_object = db_object

    def __str__(self):
        return (
            f"(model_cls={self.model_cls.__name__} raw_item_data={self.raw_item_data}"
            f" parent_model_cls={None if not self.parent_spec else self.parent_spec.model_cls}"
            f" db_object={self.db_object})"
        )


def get_raw_seed_data_from_file(seed_file_path=SEED_DATA_FILE_PATH):
    """Loads raw seed data from a seed data file"""
    with open(seed_file_path) as f:
        return json.loads(f.read())


def set_model_properties_from_dict(model_obj, property_dict):
    """
    Takes a model object and a dict property names mapped to desired values, then sets all of the relevant
    property values on the model object and saves it
    """
    for field, value in property_dict.items():
        setattr(model_obj, field, value)
    model_obj.save()
    return model_obj


def get_field_data(raw_data):
    """
    Returns key/value pairs from raw data that are meant to refer to actual model fields

    Args:
        raw_data (dict):

    Returns:
        dict:
    """
    return {
        k: v for k, v in raw_data.items() if re.match(r"^[a-zA-Z].*", k) is not None
    }


def get_own_data(raw_data):
    """
    Returns key/value pairs from raw data, excluding data that describes child objects

    Args:
        raw_data (dict):

    Returns:
        dict:
    """
    return {k: v for k, v in raw_data.items() if not k.startswith("[")}


def get_child_object_data(raw_data):
    """
    Returns key/value pairs that describe child objects in raw data

    Args:
        raw_data (dict):

    Returns:
        dict:
    """
    return {k: v for k, v in raw_data.items() if k.startswith("[")}


def seed_prefixed(value):
    """
    Returns a value with a string prepended that indicates the item is seed data.

    Args:
        value (str): The value to which the prefix should be added

    Returns:
        str: Seed-prefixed value
    """
    return f"{SEED_DATA_PREFIX}{value}"


def seed_adjusted_field_data(model_cls, raw_item_data):
    """
    Given some raw data, returns a dict with only the keys that refer to actual model fields, and if necessary,
    prefixes values to reflect that they are seed data.

    Args:
        model_cls (Type[django.db.models.Model]): The model class of the objects being described by the raw data
        raw_item_data (dict): Raw data describing an object that should be created as seed data

    Returns:
        dict:
    """
    field_data = get_field_data(raw_item_data)
    if not field_data or model_cls not in SEED_DATA_KEY_FIELDS:
        return field_data
    seeded_field_name = SEED_DATA_KEY_FIELDS[model_cls]
    if seeded_field_name not in field_data:
        return field_data
    return {
        **field_data,
        seeded_field_name: seed_prefixed(field_data[seeded_field_name]),
    }


def parse_date_range_choice(raw_data):
    """
    Given some raw data, returns a date range choice if one was defined

    Args:
        raw_data (dict): Raw data describing an object

    Returns:
        Optional(DateRangeOption): The date range choice, or None
    """
    dates_value = raw_data.get("_dates")
    if dates_value is None or not hasattr(DateRangeOption, dates_value):
        return None
    return getattr(DateRangeOption, dates_value).value


def get_date_range(
    date_range_choice=DateRangeOption.current.value,
    range_days=DEFAULT_RANGE_DAYS,
    offset_days=DEFAULT_OFFSET_DAYS,
    series_index=0,
):
    """
    Returns a date range given certain specifications, and includes some special handling for a series of date ranges.
    For example, if 3 date ranges need to be created in the future, an index can be provided to indicate the
    position in that series, and this function will create those ranges so they don't overlap.

    Examples:
        now = datetime(2020, 1, 10, 0, 0, 0)
        get_date_range(date_range_choice="past", range_days=5, offset_days=2) == \
            (datetime(2020, 1, 3, 0, 0, 0), datetime(2020, 1, 8, 0, 0, 0))
        get_date_range(date_range_choice="current", range_days=5, offset_days=2) == \
            (datetime(2020, 1, 9, 0, 0, 0), datetime(2020, 1, 14, 0, 0, 0))
        get_date_range(date_range_choice="future", range_days=5, offset_days=2) == \
            (datetime(2020, 1, 12, 0, 0, 0), datetime(2020, 1, 17, 0, 0, 0))
        get_date_range(date_range_choice="future", range_days=5, offset_days=2, series_index=1) == \
            (datetime(2020, 1, 19, 0, 0, 0), datetime(2020, 1, 24, 0, 0, 0))
        get_date_range(date_range_choice="future", range_days=5, offset_days=2, series_index=2) == \
            (datetime(2020, 1, 26, 0, 0, 0), datetime(2020, 1, 31, 0, 0, 0))

    Args:
        date_range_choice (DateRangeOption): A string indicating the type of date range desired
        range_days (int): The number of days that should be spanned by this date range
        offset_days (int): The offset of the start date of this date range from some baseline date
        series_index (int): If this date range is in a series (for example, the 2nd of 3 date ranges that
            should exist in the future), the index of this particular date range in that series.

    Returns:
        Tuple(datetime.datetime, datetime.datetime): Start and end date representing the desired date range
    """
    if series_index > 0 and date_range_choice in {
        DateRangeOption.past.value,
        DateRangeOption.future.value,
    }:
        prev_index_start_date, prev_index_end_date = get_date_range(
            date_range_choice=date_range_choice,
            range_days=range_days,
            offset_days=offset_days,
            series_index=series_index - 1,
        )
        if date_range_choice == DateRangeOption.future.value:
            baseline_date = prev_index_end_date
        else:
            baseline_date = prev_index_start_date
    else:
        baseline_date = now_in_utc()
    if date_range_choice == DateRangeOption.future.value:
        start_date = baseline_date + timedelta(days=offset_days)
    elif date_range_choice == DateRangeOption.current.value:
        start_date = baseline_date - timedelta(days=int(offset_days / 2))
    elif date_range_choice == DateRangeOption.past.value:
        start_date = (
            baseline_date - timedelta(days=offset_days) - timedelta(days=range_days)
        )
    else:
        return None, None
    end_date = start_date + timedelta(days=range_days)
    return start_date, end_date
