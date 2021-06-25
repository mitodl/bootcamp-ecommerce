"""Testing utils"""
import sys
import json
from unittest.mock import Mock
import csv
import tempfile
from importlib import reload, import_module

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls.base import clear_url_caches

from rest_framework.renderers import JSONRenderer
from rest_framework import status
from requests.exceptions import HTTPError
from mitol.common.pytest_utils import MockResponse as CommonMockResponse

from main import features


def assert_drf_json_equal(obj1, obj2):
    """
    Asserts that two objects are equal after a round trip through JSON serialization/deserialization.
    Particularly helpful when testing DRF serializers where you may get back OrderedDict and other such objects.

    Args:
        obj1 (object): the first object
        obj2 (object): the second object
    """
    json_renderer = JSONRenderer()
    converted1 = json.loads(json_renderer.render(obj1))
    converted2 = json.loads(json_renderer.render(obj2))
    assert converted1 == converted2


class MockResponse(CommonMockResponse):
    """
    Mock requests.Response
    """

    @property
    def ok(self):  # pylint: disable=missing-docstring
        return status.HTTP_200_OK <= self.status_code < status.HTTP_400_BAD_REQUEST

    def raise_for_status(self):
        """Raises an exception"""
        if not self.ok:
            raise HTTPError(response=self)


class MockHttpError(HTTPError):
    """Mocked requests.exceptions.HttpError"""

    def __init__(self, *args, **kwargs):
        response = MockResponse(content={"bad": "response"}, status_code=400)
        super().__init__(*args, **{**kwargs, **{"response": response}})


def drf_datetime(dt):
    """
    Returns a datetime formatted as a DRF DateTimeField formats it

    Args:
        dt(datetime): datetime to format

    Returns:
        str: ISO 8601 formatted datetime
    """
    return dt.isoformat().replace("+00:00", "Z")


class PickleableMock(Mock):
    """
    A Mock that can be passed to pickle.dumps()

    Source: https://github.com/testing-cabal/mock/issues/139#issuecomment-122128815
    """

    def __reduce__(self):
        """Required method for being pickleable"""
        return (Mock, ())


def create_tempfile_csv(rows_iter):
    """
    Creates a temporary CSV file for use in testing file upload views

    Args:
        rows_iter (iterable of lists): An iterable of lists of strings representing the csv values.
            Example: [["a","b","c"], ["d","e","f"]] --> CSV contents: "a,b,c\nd,e,f"

    Returns:
        SimpleUploadedFile: A temporary CSV file with the given contents
    """
    f = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
    with open(f.name, "w", encoding="utf8", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        for row in rows_iter:
            writer.writerow(row)
    with open(f.name, "r") as user_csv:
        return SimpleUploadedFile(
            f.name, user_csv.read().encode("utf8"), content_type="application/csv"
        )


def format_as_iso8601(time, remove_microseconds=True):
    """Helper function to format datetime with the Z at the end"""
    # Can't use datetime.isoformat() because format is slightly different from this
    iso_format = "%Y-%m-%dT%H:%M:%S.%f"
    # chop off microseconds to make milliseconds
    str_time = time.strftime(iso_format)
    if remove_microseconds:
        str_time = str_time[:-3]
    return str_time + "Z"


def reload_urlconf():
    """Reloads the Django URL configuration"""
    from django.conf import settings

    clear_url_caches()
    urlconf = settings.ROOT_URLCONF
    if urlconf in sys.modules:
        reload(sys.modules[urlconf])
    else:
        import_module(urlconf)


def patched_feature_enabled(patch_dict):
    """
    Returns a patched version of features.is_enabled. If the feature name is a key in the
    argument dict, it returns the value in that dict. Otherwise it just returns the result
    of features.is_enabled.

    Usage: Set as the side_effect of a patch for features.is_enabled
    mocker.patch("main.features.is_enabled", side_effect=patched_feature_enabled({MY_FEATURE: True}))

    Args:
        patch_dict (Dict[str, bool]): A dictionary containing feature names mapped to the result
          they should return if features.is_enabled is called with that feature name

    Returns:
        bool: Value indicating whether or not the feature is enabled
    """

    def _patched(*args, **kwargs):  # pylint:disable=missing-docstring
        feature_name = args[0]
        if feature_name in patch_dict:
            return patch_dict[feature_name]
        return features.is_enabled(*args, **kwargs)

    return _patched
