"""
Tests for the utils module
"""
import datetime
import operator as op
from math import ceil
from types import SimpleNamespace

import pytest
import pytz

from ecommerce.factories import Order, ReceiptFactory
from main.utils import (
    get_field_names,
    is_empty_file,
    serialize_model_object,
    chunks,
    now_in_utc,
    first_or_none,
    first_matching_item,
    is_near_now,
    get_error_response_summary,
    has_equal_properties,
    unique,
    unique_ignore_case,
    max_or_none,
    item_at_index_or_none,
    all_unique,
    all_equal,
    has_all_keys,
    is_blank,
    group_into_dict,
    filter_dict_by_key_set,
    partition_around_index,
    partition_to_lists,
    format_month_day,
)
from main.test_utils import MockResponse, format_as_iso8601


def test_now_in_utc():
    """now_in_utc() should return the current time set to the UTC time zone"""
    now = now_in_utc()
    assert is_near_now(now)
    assert now.tzinfo == pytz.UTC


def test_is_near_now():
    """
    Test is_near_now for now
    """
    now = datetime.datetime.now(tz=pytz.UTC)
    assert is_near_now(now) is True
    later = now + datetime.timedelta(0, 6)
    assert is_near_now(later) is False
    earlier = now - datetime.timedelta(0, 6)
    assert is_near_now(earlier) is False


def test_first_or_none():
    """
    Assert that first_or_none returns the first item in an iterable or None
    """
    assert first_or_none([]) is None
    assert first_or_none(set()) is None
    assert first_or_none([1, 2, 3]) == 1
    assert first_or_none(range(1, 5)) == 1


def test_first_matching_item():
    """first_matching_item should return the first item where the predicate function returns true"""
    assert first_matching_item([1, 2, 3, 4, 5], lambda x: x % 2 == 0) == 2
    assert first_matching_item([], lambda x: True) is None
    assert first_matching_item(["x", "y", "z"], lambda x: False) is None


def test_max_or_none():
    """
    Assert that max_or_none returns the max of some iterable, or None if the iterable has no items
    """
    assert max_or_none(i for i in [5, 4, 3, 2, 1]) == 5
    assert max_or_none([1, 3, 5, 4, 2]) == 5
    assert max_or_none([]) is None


def test_unique():
    """
    Assert that unique() returns a generator of unique elements from a provided iterable
    """
    assert list(unique([1, 2, 2, 3, 3, 0, 3])) == [1, 2, 3, 0]
    assert list(unique(("a", "b", "a", "c", "C", None))) == ["a", "b", "c", "C", None]


def test_unique_ignore_case():
    """
    Assert that unique_ignore_case() returns a generator of unique lowercase strings from a
    provided iterable
    """
    assert list(unique_ignore_case(["ABC", "def", "AbC", "DEf"])) == ["abc", "def"]


def test_item_at_index_or_none():
    """
    Assert that item_at_index_or_none returns an item at a given index, or None if that index
    doesn't exist
    """
    arr = [1, 2, 3]
    assert item_at_index_or_none(arr, 1) == 2
    assert item_at_index_or_none(arr, 10) is None


def test_all_equal():
    """
    Assert that all_equal returns True if all of the provided args are equal to each other
    """
    assert all_equal(1, 1, 1) is True
    assert all_equal(1, 2, 1) is False
    assert all_equal() is True


def test_all_unique():
    """
    Assert that all_unique returns True if all of the items in the iterable argument are unique
    """
    assert all_unique([1, 2, 3, 4]) is True
    assert all_unique((1, 2, 3, 4)) is True
    assert all_unique([1, 2, 3, 1]) is False


def test_has_all_keys():
    """
    Assert that has_all_keys returns True if the given dict has all of the specified keys
    """
    d = {"a": 1, "b": 2, "c": 3}
    assert has_all_keys(d, ["a", "c"]) is True
    assert has_all_keys(d, ["a", "z"]) is False


def test_is_blank():
    """
    Assert that is_blank returns True if the given value is None or a blank string
    """
    assert is_blank("") is True
    assert is_blank(None) is True
    assert is_blank(0) is False
    assert is_blank(" ") is False
    assert is_blank(False) is False
    assert is_blank("value") is False


def test_group_into_dict():
    """
    Assert that group_into_dict takes an iterable of items and returns a dictionary of those items
    grouped by generated keys
    """

    class Car:  # pylint: disable=missing-docstring
        def __init__(self, make, model):
            self.make = make
            self.model = model

    cars = [
        Car(make="Honda", model="Civic"),
        Car(make="Honda", model="Accord"),
        Car(make="Ford", model="F150"),
        Car(make="Ford", model="Focus"),
        Car(make="Jeep", model="Wrangler"),
    ]
    grouped_cars = group_into_dict(cars, key_fn=op.attrgetter("make"))
    assert set(grouped_cars.keys()) == {"Honda", "Ford", "Jeep"}
    assert set(grouped_cars["Honda"]) == set(cars[0:2])
    assert set(grouped_cars["Ford"]) == set(cars[2:4])
    assert grouped_cars["Jeep"] == [cars[4]]

    nums = [1, 2, 3, 4, 5, 6]
    grouped_nums = group_into_dict(nums, key_fn=lambda num: (num % 2 == 0))
    assert grouped_nums.keys() == {True, False}
    assert set(grouped_nums[True]) == {2, 4, 6}
    assert set(grouped_nums[False]) == {1, 3, 5}


def test_filter_dict_by_key_set():
    """
    Test that filter_dict_by_key_set returns a dict with only the given keys
    """
    d = {"a": 1, "b": 2, "c": 3, "d": 4}
    assert filter_dict_by_key_set(d, {"a", "c"}) == {"a": 1, "c": 3}
    assert filter_dict_by_key_set(d, {"a", "c", "nonsense"}) == {"a": 1, "c": 3}
    assert filter_dict_by_key_set(d, {"nonsense"}) == {}


def test_partition_to_lists():
    """
    Assert that partition_to_lists splits an iterable into two lists according to a condition
    """
    nums = [1, 2, 1, 3, 1, 4, 0, None, None]
    not_ones, ones = partition_to_lists(nums, lambda n: n == 1)
    assert not_ones == [2, 3, 4, 0, None, None]
    assert ones == [1, 1, 1]
    # The default predicate is the standard Python bool() function
    falsey, truthy = partition_to_lists(nums)
    assert falsey == [0, None, None]
    assert truthy == [1, 2, 1, 3, 1, 4]


def test_partition_around_index():
    """partition_around_index should split a list into two lists around an index"""
    assert partition_around_index([1, 2, 3, 4], 2) == ([1, 2], [4])
    assert partition_around_index([1, 2, 3, 4], 0) == ([], [2, 3, 4])
    assert partition_around_index([1, 2, 3, 4], 3) == ([1, 2, 3], [])
    with pytest.raises(ValueError):
        partition_around_index([1, 2, 3, 4], 4)


@pytest.mark.parametrize(
    "content,content_type,exp_summary_content,exp_url_in_summary",
    [
        ['{"bad": "response"}', "application/json", '{"bad": "response"}', False],
        ["plain text", "text/plain", "plain text", False],
        [
            "<div>HTML content</div>",
            "text/html; charset=utf-8",
            "(HTML body ignored)",
            True,
        ],
    ],
)
def test_get_error_response_summary(
    content, content_type, exp_summary_content, exp_url_in_summary
):
    """
    get_error_response_summary should provide a summary of an error HTTP response object with the correct bits of
    information depending on the type of content.
    """
    status_code = 400
    url = "http://example.com"
    mock_response = MockResponse(
        status_code=status_code, content=content, content_type=content_type, url=url
    )
    summary = get_error_response_summary(mock_response)
    assert f"Response - code: {status_code}" in summary
    assert f"content: {exp_summary_content}" in summary
    assert (f"url: {url}" in summary) is exp_url_in_summary


@pytest.mark.django_db
def test_jsonfield(settings):
    """
    Test a model with a JSONField is handled correctly
    """
    settings.CYBERSOURCE_SECURITY_KEY = "asdf"
    receipt = ReceiptFactory.create()
    assert serialize_model_object(receipt) == {
        "created_on": format_as_iso8601(receipt.created_on),
        "data": receipt.data,
        "id": receipt.id,
        "updated_on": format_as_iso8601(receipt.updated_on),
        "order": receipt.order.id,
    }


def test_get_field_names():
    """
    Assert that get_field_names does not include related fields
    """
    assert set(get_field_names(Order)) == {
        "user",
        "status",
        "total_price_paid",
        "application",
        "created_on",
        "updated_on",
        "payment_type",
    }


def test_is_empty_file():
    """is_empty_file should return True if the given object is None or has a blank name property"""
    fake_file = None
    assert is_empty_file(fake_file) is True
    fake_file = SimpleNamespace(name="")
    assert is_empty_file(fake_file) is True
    fake_file = SimpleNamespace(name="path/to/file.txt")
    assert is_empty_file(fake_file) is False


def test_chunks():
    """
    test for chunks
    """
    input_list = list(range(113))
    output_list = []
    for nums in chunks(input_list):
        output_list += nums
    assert output_list == input_list

    output_list = []
    for nums in chunks(input_list, chunk_size=1):
        output_list += nums
    assert output_list == input_list

    output_list = []
    for nums in chunks(input_list, chunk_size=124):
        output_list += nums
    assert output_list == input_list


def test_chunks_iterable():
    """
    test that chunks works on non-list iterables too
    """
    count = 113
    input_range = range(count)
    chunk_output = []
    for chunk in chunks(input_range, chunk_size=10):
        chunk_output.append(chunk)
    assert len(chunk_output) == ceil(113 / 10)

    range_list = []
    for chunk in chunk_output:
        range_list += chunk
    assert range_list == list(range(count))


def test_format_month_day():
    """
    format_month_day should format the month and day from a datetime
    """
    dt = datetime.datetime(year=2020, month=1, day=1, tzinfo=pytz.UTC)
    assert format_month_day(dt) == "Jan 1"
    assert format_month_day(dt, month_fmt="%b") == "Jan 1"
    assert format_month_day(dt, month_fmt="%B") == "January 1"


def test_has_equal_properties():
    """
    Assert that has_equal_properties returns True if an object has equivalent properties to a given dict
    """
    obj = SimpleNamespace(a=1, b=2, c=3)
    assert has_equal_properties(obj, {}) is True
    assert has_equal_properties(obj, dict(a=1, b=2)) is True
    assert has_equal_properties(obj, dict(a=1, b=2, c=3)) is True
    assert has_equal_properties(obj, dict(a=2)) is False
    assert has_equal_properties(obj, dict(d=4)) is False
