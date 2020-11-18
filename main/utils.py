"""
General bootcamp utility functions
"""
import datetime
import itertools
import json
import logging
import os
import re
import pytz

from django.conf import settings
from django.core.serializers import serialize
from rest_framework import serializers


log = logging.getLogger(__name__)


def is_near_now(time):
    """
    Returns true if time is within five seconds or so of now
    Args:
        time (datetime.datetime):
            The time to test
    Returns:
        bool:
            True if near now, false otherwise
    """
    now = datetime.datetime.now(tz=pytz.UTC)
    five_seconds = datetime.timedelta(0, 5)
    return now - five_seconds < time < now + five_seconds


def first_or_none(iterable):
    """
    Returns the first item in an iterable, or None if the iterable is empty

    Args:
        iterable (iterable): Some iterable
    Returns:
        first item or None
    """
    return next((x for x in iterable), None)


def first_matching_item(iterable, predicate):
    """
    Gets the first item in an iterable that matches a predicate (or None if nothing matches)

    Returns:
        Matching item or None
    """
    return next(filter(predicate, iterable), None)


def max_or_none(iterable):
    """
    Returns the max of some iterable, or None if the iterable has no items

    Args:
        iterable (iterable): Some iterable
    Returns:
        max item or None
    """
    try:
        return max(iterable)
    except ValueError:
        return None


def partition(items, predicate=bool):
    """
    Partitions an iterable into two different iterables - the first does not match the given condition, and the second
    does match the given condition.

    Args:
        items (iterable): An iterable of items to partition
        predicate (function): A function that takes each item and returns True or False
    Returns:
        tuple of iterables: An iterable of non-matching items, paired with an iterable of matching items
    """
    a, b = itertools.tee((predicate(item), item) for item in items)
    return (item for pred, item in a if not pred), (item for pred, item in b if pred)


def partition_to_lists(items, predicate=bool):
    """
    Partitions an iterable into two different lists - the first does not match the given condition, and the second
    does match the given condition.

    Args:
        items (iterable): An iterable of items to partition
        predicate (function): A function that takes each item and returns True or False
    Returns:
        tuple of lists: A list of non-matching items, paired with a list of matching items
    """
    a, b = partition(items, predicate=predicate)
    return list(a), list(b)


def partition_around_index(list_to_partition, index):
    """
    Partitions a list around the given index, returning 2 lists. The first contains elements
    before the index, and the second contains elements after the index (the given index is excluded).

    Examples:
        partition_around_index([1,2,3,4,5], 2) == ([1,2], [4,5])
        partition_around_index([1,2,3,4,5], 0) == ([], [2,3,4,5])

    Args:
        list_to_partition (list): The list to partition
        index (int): The index that the list should be partitioned around

    Returns:
        Tuple(list, list): The partitions of the given list
    """
    list_len = len(list_to_partition)
    if list_len <= index:
        raise ValueError(
            "Index out of range: {} ({} item list)".format(index, list_len)
        )
    l1, l2 = [], []
    if index > 0:
        l1 = list_to_partition[0:index]
    if index < (list_len - 1):
        l2 = list_to_partition[(index + 1) :]
    return l1, l2


def unique(iterable):
    """
    Returns a generator containing all unique items in an iterable

    Args:
        iterable (iterable): An iterable of any hashable items
    Returns:
        generator: Unique items in the given iterable
    """
    seen = set()
    return (x for x in iterable if x not in seen and not seen.add(x))


def unique_ignore_case(strings):
    """
    Returns a generator containing all unique strings (coerced to lowercase) in a given iterable

    Args:
        strings (iterable of str): An iterable of strings
    Returns:
        generator: Unique lowercase strings in the given iterable
    """
    seen = set()
    return (s for s in map(str.lower, strings) if s not in seen and not seen.add(s))


def item_at_index_or_none(indexable, index):
    """
    Returns the item at a certain index, or None if that index doesn't exist

    Args:
        indexable (list or tuple):
        index (int): The index in the list or tuple

    Returns:
        The item at the given index, or None
    """
    try:
        return indexable[index]
    except IndexError:
        return None


def all_equal(*args):
    """
    Returns True if all of the provided args are equal to each other

    Args:
        *args (hashable): Arguments of any hashable type

    Returns:
        bool: True if all of the provided args are equal, or if the args are empty
    """
    return len(set(args)) <= 1


def all_unique(iterable):
    """
    Returns True if all of the provided args are equal to each other

    Args:
        iterable: An iterable of hashable items

    Returns:
        bool: True if all of the provided args are equal
    """
    return len(set(iterable)) == len(iterable)


def has_all_keys(dict_to_scan, keys):
    """
    Returns True if the given dict has all of the given keys

    Args:
        dict_to_scan (Dict[str, Any]):
        keys (Iterable[str]): Iterable of keys to check for

    Returns:
        bool: True if the given dict has all of the given keys
    """
    return all(key in dict_to_scan for key in keys)


def is_blank(value):
    """
    Checks if the given value is None or a blank string

    Args:
        value (Optional[Any]): The value to check

    Returns:
        bool: True if the value is None or a blank string
    """
    return value is None or value == ""


def group_into_dict(items, key_fn):
    """
    Groups items into a dictionary based on a key generated by a given function

    Examples:
        items = [
            Car(make="Honda", model="Civic"),
            Car(make="Honda", model="Accord"),
            Car(make="Ford", model="F150"),
            Car(make="Ford", model="Focus"),
        ]
        group_into_dict(items, lambda car: car.make) == {
            "Honda": [Car(make="Honda", model="Civic"), Car(make="Honda", model="Accord")],
            "Ford": [Car(make="Ford", model="F150"), Car(make="Ford", model="Focus")],
        }

    Args:
        items (iterable of any): An iterable of objects to group into a dictionary
        key_fn (function): A function that will take an individual item and produce a dict key

    Returns:
        dict: A dictionary with keys produced by the key function paired with a list of all the given
            items that produced that key.
    """
    sorted_items = sorted(items, key=key_fn)
    return {
        key: list(values_iter)
        for key, values_iter in itertools.groupby(sorted_items, key=key_fn)
    }


def webpack_dev_server_host(request):
    """
    Get the correct webpack dev server host
    """
    return settings.WEBPACK_DEV_SERVER_HOST or request.get_host().split(":")[0]


def webpack_dev_server_url(request):
    """
    Get the full URL where the webpack dev server should be running
    """
    return "http://{}:{}".format(
        webpack_dev_server_host(request), settings.WEBPACK_DEV_SERVER_PORT
    )


def now_in_utc():
    """
    Get the current time in UTC
    Returns:
        datetime.datetime: A datetime object for the current time
    """
    return datetime.datetime.now(tz=pytz.UTC)


def serialize_model_object(obj):
    """
    Serialize model into a dict representable as JSON

    Args:
        obj (django.db.models.Model): An instantiated Django model
    Returns:
        dict:
            A representation of the model
    """
    # serialize works on iterables so we need to wrap object in a list, then unwrap it
    data = json.loads(serialize("json", [obj]))[0]
    serialized = data["fields"]
    serialized["id"] = data["pk"]
    return serialized


def get_field_names(model):
    """
    Get field names which aren't autogenerated

    Args:
        model (class extending django.db.models.Model): A Django model class
    Returns:
        list of str:
            A list of field names
    """
    return [
        field.name
        for field in model._meta.get_fields()
        if not field.auto_created  # pylint: disable=protected-access
    ]


def is_empty_file(file_field):
    """
    Return True if the given file field object passed in is None or has no filename

    Args:
        file_field (django.db.models.FileField or None): A file field property of a model object

    Returns:
        bool: True if the given file field object passed in is None or has no filename
    """
    return file_field is None or not file_field.name


def filter_dict_by_key_set(dict_to_filter, key_set):
    """Takes a dictionary and returns a copy with only the keys that exist in the given set"""
    return {key: dict_to_filter[key] for key in dict_to_filter.keys() if key in key_set}


def get_filename_from_path(filepath):
    """
    Returns a filename without a directory path

    Args:
        filepath (str): The file path (e.g.: "/path/to/file.txt")

    Returns:
        str: The filename without the directory path (e.g.: "file.txt")
    """
    return os.path.split(filepath)[1]


def chunks(iterable, chunk_size=20):
    """
    Yields chunks of an iterable as sub lists each of max size chunk_size.

    Args:
        iterable (iterable): iterable of elements to chunk
        chunk_size (int): Max size of each sublist

    Yields:
        list: List containing a slice of list_to_chunk
    """
    chunk_size = max(1, chunk_size)
    iterable = iter(iterable)
    chunk = list(itertools.islice(iterable, chunk_size))

    while len(chunk) > 0:
        yield chunk
        chunk = list(itertools.islice(iterable, chunk_size))


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def get_error_response_summary(response):
    """
    Returns a summary of an error raised from a failed HTTP request using the requests library

    Args:
        response (requests.models.Response): The requests library response object

    Returns:
        str: A summary of the error response
    """
    # If the response is an HTML document, include the URL in the summary but not the raw HTML
    if "text/html" in response.headers.get("Content-Type", ""):
        summary_dict = {"url": response.url, "content": "(HTML body ignored)"}
    else:
        summary_dict = {"content": response.text}
    summary_dict_str = ", ".join([f"{k}: {v}" for k, v in summary_dict.items()])
    return f"Response - code: {response.status_code}, {summary_dict_str}"


def serializer_date_format(dt):
    """
    Helper function to return a date formatted in the same way that our serializers

    Args:
        dt (Optional[datetime.datetime]): The datetime object (or None)

    Returns:
        Optional[str]: The string representing the datetime (or None)
    """
    return serializers.DateTimeField().to_representation(dt)
