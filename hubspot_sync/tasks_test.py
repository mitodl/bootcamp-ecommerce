"""
Tests for hubspot_sync tasks
"""
# pylint: disable=redefined-outer-name
import pytest

from mitol.hubspot_api.factories import SimplePublicObjectFactory

from hubspot_sync import tasks


pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "task_func",
    [
        "sync_contact_with_hubspot",
        "sync_product_with_hubspot",
        "sync_deal_with_hubspot",
    ],
)
def test_task_functions(mocker, task_func):
    """These task functions should call the api function of the same name and return a hubspot id"""
    mock_result = SimplePublicObjectFactory()
    mock_api_call = mocker.patch(
        f"hubspot_sync.tasks.api.{task_func}", return_value=mock_result
    )
    mock_object_id = 101
    assert getattr(tasks, task_func)(mock_object_id) == mock_result.id
    mock_api_call.assert_called_once_with(mock_object_id)
