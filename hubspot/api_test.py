"""
Hubspot API tests
"""
# pylint: disable=redefined-outer-name
import abc
from unittest.mock import Mock
from urllib.parse import urlencode

import pytest
from django.http import HttpResponse
from django.conf import settings
from faker import Faker
from requests import HTTPError

from hubspot import api

from profiles.factories import ProfileFactory
from profiles.serializers import UserSerializer

fake = Faker()

test_object_type = "deals"


# Taken from mitxpro
def any_instance_of(*cls):
    """
    Returns a type that evaluates __eq__ in isinstance terms

    Args:
        cls (list of types): variable list of types to ensure equality against

    Returns:
        AnyInstanceOf: dynamic class type with the desired equality
    """

    class AnyInstanceOf(metaclass=abc.ABCMeta):
        """Dynamic class type for __eq__ in terms of isinstance"""

        def __eq__(self, other):
            return isinstance(other, cls)

    for c in cls:
        AnyInstanceOf.register(c)
    return AnyInstanceOf()


@pytest.fixture
def property_group():
    """ Return sample group JSON """
    return {"name": "group_name", "label": "Group Label"}


@pytest.mark.parametrize("request_method", ["GET", "PUT", "POST"])
@pytest.mark.parametrize(
    "endpoint,api_url,expected_url",
    [
        [
            "sync-errors",
            "/extensions/ecomm/v1",
            f"{api.HUBSPOT_API_BASE_URL}/extensions/ecomm/v1/sync-errors",
        ],
        [
            "",
            "/extensions/ecomm/v1/installs",
            f"{api.HUBSPOT_API_BASE_URL}/extensions/ecomm/v1/installs",
        ],
        [
            "CONTACT",
            "/extensions/ecomm/v1/sync-messages",
            f"{api.HUBSPOT_API_BASE_URL}/extensions/ecomm/v1/sync-messages/CONTACT",
        ],
    ],
)
def test_send_hubspot_request(mocker, request_method, endpoint, api_url, expected_url):
    """Test sending hubspot request with method = GET"""
    value = fake.pyint()
    query_params = {"param": value}

    # Include hapikey when generating url to match request call against
    full_query_params = {"param": value, "hapikey": settings.HUBSPOT_API_KEY}
    mock_request = mocker.patch(f"hubspot.api.requests.{request_method.lower()}")
    url_params = urlencode(full_query_params)
    url = f"{expected_url}?{url_params}"
    if request_method == "GET":
        api.send_hubspot_request(
            endpoint, api_url, request_method, query_params=query_params
        )
        mock_request.assert_called_once_with(url=url)
    else:
        body = fake.pydict()
        api.send_hubspot_request(
            endpoint, api_url, request_method, query_params=query_params, body=body
        )
        mock_request.assert_called_once_with(url=url, json=body)


def test_send_hubspot_request_try_again(mocker):
    """Test the try again decorator"""
    mock_request = mocker.patch(f"hubspot.api.requests.get", return_value=Mock(
        raise_for_status=Mock(side_effect=HTTPError())))

    api.send_hubspot_request(
        "sync-errors", "/extensions/ecomm/v1", "GET"
    )
    assert mock_request.call_count == 3


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"prop": 1, "blank": None}, {"prop": 1, "blank": ""}),
        ({"prop": 1}, {"prop": 1}),
        ({"blank": None}, {"blank": ""}),
        ({}, {}),
    ],
)
def test_sanitize_properties(value, expected):
    """Test that sanitize_properties replaces Nones with empty strings"""
    assert api.sanitize_properties(value) == expected


def test_make_sync_message():
    """Test make_sync_message produces a properly formatted sync-message"""
    object_id = fake.pyint()
    value = fake.word()
    properties = {"prop": value, "blank": None}
    sync_message = api.make_sync_message(object_id, properties)
    assert sync_message == (
        {
            "integratorObjectId": "{}-{}".format(settings.HUBSPOT_ID_PREFIX, object_id),
            "action": "UPSERT",
            "changeOccurredTimestamp": any_instance_of(int),
            "propertyNameToValues": {"prop": value, "blank": ""},
        }
    )


@pytest.mark.django_db
def test_make_contact_sync_message():
    """Test make_contact_sync_message serializes a profile and returns a properly formatted sync message"""
    profile = ProfileFactory.create(smapply_id=123456)
    contact_sync_message = api.make_contact_sync_message(profile.user.id)
    serialized_user = UserSerializer(instance=profile.user).data
    serialized_user.update(serialized_user.pop("legal_address") or {})
    serialized_user.update(serialized_user.pop("profile") or {})
    serialized_user["street_address"] = "\n".join(serialized_user.pop("street_address"))
    assert contact_sync_message == [
        {
            "integratorObjectId": "{}-{}".format(settings.HUBSPOT_ID_PREFIX, profile.user.id),
            "action": "UPSERT",
            "changeOccurredTimestamp": any_instance_of(int),
            "propertyNameToValues": api.sanitize_properties(serialized_user),
        }
    ]


@pytest.mark.parametrize("offset", [0, 10])
def test_get_sync_errors(mock_hubspot_errors, offset):
    """Test that paging works for get_sync_errors"""
    limit = 2
    errors = list(api.get_sync_errors(limit, offset))
    assert len(errors) == 4
    mock_hubspot_errors.assert_any_call(limit, offset)
    mock_hubspot_errors.assert_any_call(limit, offset + limit)
    mock_hubspot_errors.assert_any_call(limit, offset + limit * 2)


@pytest.mark.parametrize(
    "sync_status, exists",
    [
        [HTTPError(response=HttpResponse(status=400)), False],
        [[{"hubspotId": None}], False],
        [[{"hubspotId": 3}], True],
    ],
)
def test_exists_in_hubspot(mocker, sync_status, exists):
    """Test that exists_in_hubspot return True if an object has a hubspot ID and False otherwise"""
    mock_get_sync_status = mocker.patch(
        "hubspot.api.get_sync_status", side_effect=sync_status
    )
    assert api.exists_in_hubspot("OBJECT", 1) == exists
    mock_get_sync_status.assert_called_once_with("OBJECT", 1)


@pytest.mark.parametrize(
    "property_status, exists",
    [
        [HTTPError(response=HttpResponse(status=400)), False],
        [HttpResponse(status=200), True],
    ],
)
def test_object_property_exists(mocker, property_status, exists):
    """Test that object_property_exists returns True if the property exists and False otherwise"""
    mock_get_object_property = mocker.patch(
        "hubspot.api.get_object_property", side_effect=property_status
    )
    assert api.object_property_exists("deals", "my_property") == exists
    mock_get_object_property.assert_called_once_with("deals", "my_property")


@pytest.mark.parametrize(
    "group_status, exists",
    [
        [HTTPError(response=HttpResponse(status=400)), False],
        [HttpResponse(status=200), True],
    ],
)
def test_property_group_exists(mocker, group_status, exists):
    """Test that property_group_exists returns True if the group exists and False otherwise"""
    mock_get_property_group = mocker.patch(
        "hubspot.api.get_property_group", side_effect=group_status
    )
    assert api.property_group_exists("deals", "my_group") == exists
    mock_get_property_group.assert_called_once_with("deals", "my_group")


def test_get_property_group(mock_hubspot_api_request, property_group):
    """ get_property_group should call send_hubspot_request with the correct arguments"""
    group_name = property_group["name"]
    api.get_property_group(test_object_type, group_name)
    assert mock_hubspot_api_request.called_with(
        group_name, f"/properties/v1/{test_object_type}/groups/named", "GET"
    )


def test_get_object_property(mock_hubspot_api_request):
    """ get_object_property should call send_hubspot_request with the correct arguments"""
    property_name = "y"
    api.get_object_property(test_object_type, property_name)
    assert mock_hubspot_api_request.called_with(
        f"named/{property_name}", f"/properties/v1/{test_object_type}/properties", "GET"
    )


@pytest.mark.parametrize("is_valid", [True, False])
@pytest.mark.parametrize("object_exists", [True, False])
def test_sync_object_property(
    mocker, mock_hubspot_api_request, object_exists, is_valid
):
    """sync_object_property should call send_hubspot_request with the correct arguments"""
    mocker.patch("hubspot.api.object_property_exists", return_value=object_exists)
    mock_property = {
        "name": "property_name",
        "label": "Property Label",
        "groupName": "Property Group",
        "description": "Property description",
        "field_type": "text",
        "type": "string",
    }

    if not is_valid:
        mock_property.pop("name")
        with pytest.raises(KeyError):
            api.sync_object_property(test_object_type, mock_property)
    else:
        api.sync_object_property(test_object_type, mock_property)
        if object_exists:
            assert mock_hubspot_api_request.called_with(
                f"named/{mock_property['name']}",
                f"/properties/v1/{test_object_type}/properties",
                "PUT",
                mock_property,
            )
        else:
            assert mock_hubspot_api_request.called_with(
                "",
                f"/properties/v1/{test_object_type}/properties",
                "POST",
                mock_property,
            )


@pytest.mark.parametrize("object_exists", [True, False])
def test_sync_property_group(
    mocker, mock_hubspot_api_request, object_exists, property_group
):
    """sync_object_property should call send_hubspot_request with the correct arguments"""
    mocker.patch("hubspot.api.object_property_exists", return_value=object_exists)
    group_name = property_group["name"]
    group_label = property_group["label"]
    api.sync_property_group(test_object_type, group_name, group_label)
    if object_exists:
        assert mock_hubspot_api_request.called_with(
            f"named/{group_name}",
            f"/properties/v1/{test_object_type}/groups",
            "PUT",
            property_group,
        )
    else:
        assert mock_hubspot_api_request.called_with(
            "", f"/properties/v1/{test_object_type}/groups", "POST", property_group
        )


def test_delete_property_group(mock_hubspot_api_request, property_group):
    """ delete_property_group should call send_hubspot_request with the correct arguments"""
    api.delete_object_property(test_object_type, property_group["name"])
    assert mock_hubspot_api_request.called_with(
        f"named/{property_group['name']}",
        f"/properties/v1/{test_object_type}/groups",
        "DELETE",
    )


def test_delete_object_property(mock_hubspot_api_request, property_group):
    """ delete_object_property should call send_hubspot_request with the correct arguments"""
    api.delete_object_property(test_object_type, property_group["name"])
    assert mock_hubspot_api_request.called_with(
        f"named/{ property_group['name']}",
        f"/properties/v1/{test_object_type}/groups",
        "DELETE",
    )
