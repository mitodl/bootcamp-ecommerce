"""
Tests for hubspot_sync tasks
"""
# pylint: disable=redefined-outer-name
import pytest
from django.contrib.contenttypes.models import ContentType
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation
from hubspot.crm.objects import ApiException, BatchInputSimplePublicObjectInput
from mitol.hubspot_api.api import HubspotAssociationType, HubspotObjectType
from mitol.hubspot_api.exceptions import TooManyRequestsException
from mitol.hubspot_api.factories import HubspotObjectFactory, SimplePublicObjectFactory
from mitol.hubspot_api.models import HubspotObject

from applications.factories import BootcampApplicationFactory
from hubspot_sync import tasks
from hubspot_sync.api import make_contact_sync_message
from hubspot_sync.tasks import (
    batch_upsert_associations,
    batch_upsert_associations_chunked,
)
from klasses.factories import BootcampRunFactory
from klasses.models import BootcampRun
from profiles.factories import UserFactory

pytestmark = [pytest.mark.django_db]


SYNC_FUNCTIONS = [
    "sync_contact_with_hubspot",
    "sync_product_with_hubspot",
    "sync_deal_with_hubspot",
]


@pytest.mark.parametrize("task_func", SYNC_FUNCTIONS)
def test_task_functions(mocker, task_func):
    """These task functions should call the api function of the same name and return a hubspot id"""
    mock_result = SimplePublicObjectFactory()
    mock_api_call = mocker.patch(
        f"hubspot_sync.tasks.api.{task_func}", return_value=mock_result
    )
    mock_object_id = 101
    assert getattr(tasks, task_func)(mock_object_id) == mock_result.id
    mock_api_call.assert_called_once_with(mock_object_id)


@pytest.mark.parametrize("task_func", SYNC_FUNCTIONS)
@pytest.mark.parametrize(
    "status, expected_error", [[429, TooManyRequestsException], [500, ApiException]]
)
def test_task_functions_error(mocker, task_func, status, expected_error):
    """These task functions should return the expected exception class"""
    mocker.patch(
        f"hubspot_sync.tasks.api.{task_func}", side_effect=expected_error(status=status)
    )
    with pytest.raises(expected_error):
        getattr(tasks, task_func)(101)


@pytest.mark.parametrize("create", [True, False])
def test_batch_upsert_hubspot_objects(settings, mocker, mocked_celery, create):
    """batch_upsert_hubspot_objects should call batch_upsert_hubspot_objects_chunked w/correct args"""
    settings.HUBSPOT_MAX_CONCURRENT_TASKS = 4
    mock_create = mocker.patch(
        "hubspot_sync.tasks.batch_create_hubspot_objects_chunked.s"
    )
    mock_update = mocker.patch(
        "hubspot_sync.tasks.batch_update_hubspot_objects_chunked.s"
    )
    unsynced_products = BootcampRunFactory.create_batch(2)
    synced_products = BootcampRunFactory.create_batch(103)
    content_type = ContentType.objects.get_for_model(BootcampRun)
    hs_objects = [
        HubspotObjectFactory.create(
            content_type=content_type, object_id=product.id, content_object=product
        )
        for product in synced_products
    ]
    with pytest.raises(TabError):
        tasks.batch_upsert_hubspot_objects.delay(
            HubspotObjectType.PRODUCTS.value, "bootcamprun", "klasses", create=create
        )
    mocked_celery.replace.assert_called_once()
    if create:
        assert mock_create.call_count == 2
        mock_create.assert_any_call(
            HubspotObjectType.PRODUCTS.value, "bootcamprun", [unsynced_products[0].id]
        )
        mock_create.assert_any_call(
            HubspotObjectType.PRODUCTS.value, "bootcamprun", [unsynced_products[1].id]
        )
        mock_update.assert_not_called()
    else:
        assert mock_update.call_count == 4
        mock_update.assert_any_call(
            HubspotObjectType.PRODUCTS.value,
            "bootcamprun",
            [
                (hso.object_id, hso.hubspot_id)
                for hso in sorted(hs_objects, key=lambda o: o.object_id)[
                    0:26
                ]  # 103/4 == 26
            ],
        )
        mock_create.assert_not_called()


def test_batch_update_hubspot_objects_with_ids(settings, mocker, mocked_celery):
    """batch_upsert_hubspot_objects should call batch_upsert_hubspot_objects_chunked w/specified ids"""
    settings.HUBSPOT_MAX_CONCURRENT_TASKS = 2
    mock_update = mocker.patch(
        "hubspot_sync.tasks.batch_update_hubspot_objects_chunked.s"
    )
    synced_products = BootcampRunFactory.create_batch(8)
    content_type = ContentType.objects.get_for_model(BootcampRun)
    hs_objects = [
        HubspotObjectFactory.create(
            content_type=content_type, object_id=product.id, content_object=product
        )
        for product in synced_products
    ]
    object_ids = sorted([(obj.object_id, obj.hubspot_id) for obj in hs_objects])
    with pytest.raises(TabError):
        tasks.batch_upsert_hubspot_objects.delay(
            HubspotObjectType.PRODUCTS.value,
            "bootcamprun",
            "klasses",
            create=False,
            object_ids=[obj[0] for obj in object_ids[0:4]],
        )
    mocked_celery.replace.assert_called_once()
    assert mock_update.call_count == 2
    mock_update.assert_any_call(
        HubspotObjectType.PRODUCTS.value, "bootcamprun", object_ids[0:2]
    )
    mock_update.assert_any_call(
        HubspotObjectType.PRODUCTS.value, "bootcamprun", object_ids[2:4]
    )


def test_batch_create_hubspot_objects_with_ids(settings, mocker, mocked_celery):
    """batch_upsert_hubspot_objects should call batch_upsert_hubspot_objects_chunked w/specified ids"""
    settings.HUBSPOT_MAX_CONCURRENT_TASKS = 2
    mock_create = mocker.patch(
        "hubspot_sync.tasks.batch_create_hubspot_objects_chunked.s"
    )
    object_ids = [8, 5, 7, 6]
    with pytest.raises(TabError):
        tasks.batch_upsert_hubspot_objects.delay(
            HubspotObjectType.PRODUCTS.value,
            "bootcamprun",
            "klasses",
            object_ids=object_ids,
        )
    mocked_celery.replace.assert_called_once()
    assert mock_create.call_count == 2
    mock_create.assert_any_call(HubspotObjectType.PRODUCTS.value, "bootcamprun", [5, 6])
    mock_create.assert_any_call(HubspotObjectType.PRODUCTS.value, "bootcamprun", [7, 8])


@pytest.mark.parametrize("id_count", [5, 15])
def test_batch_update_hubspot_objects_chunked(mocker, id_count):
    """batch_update_hubspot_objects_chunked should make expected api calls and args"""
    contacts = UserFactory.create_batch(id_count)
    mock_ids = sorted(
        list(
            zip(
                [contact.id for contact in contacts],
                [f"10001{i}" for i in range(id_count)],
            )
        )
    )
    mock_hubspot_api = mocker.patch("hubspot_sync.tasks.HubspotApi")
    mock_hubspot_api.return_value.crm.objects.batch_api.update.return_value = (
        mocker.Mock(
            results=[SimplePublicObjectFactory(id=mock_id[1]) for mock_id in mock_ids]
        )
    )
    expected_batches = 1 if id_count == 5 else 2
    tasks.batch_update_hubspot_objects_chunked(
        HubspotObjectType.CONTACTS.value, "user", mock_ids
    )
    assert (
        mock_hubspot_api.return_value.crm.objects.batch_api.update.call_count
        == expected_batches
    )
    mock_hubspot_api.return_value.crm.objects.batch_api.update.assert_any_call(
        HubspotObjectType.CONTACTS.value,
        BatchInputSimplePublicObjectInput(
            inputs=[
                {
                    "id": mock_id[1],
                    "properties": make_contact_sync_message(mock_id[0]).properties,
                }
                for mock_id in mock_ids[0 : min(id_count, 10)]
            ]
        ),
    )


@pytest.mark.parametrize(
    "status, expected_error", [[429, TooManyRequestsException], [500, ApiException]]
)
def test_batch_update_hubspot_objects_chunked_error(mocker, status, expected_error):
    """batch_update_hubspot_objects_chunked should raise expected exception"""
    mock_hubspot_api = mocker.patch("hubspot_sync.tasks.HubspotApi")
    mock_hubspot_api.return_value.crm.objects.batch_api.update.side_effect = (
        ApiException(status=status)
    )
    mock_sync_contacts = mocker.patch(
        "hubspot_sync.tasks.api.sync_contact_with_hubspot",
        side_effect=(ApiException(status=status)),
    )
    chunk = [(user.id, "123") for user in UserFactory.create_batch(3)]
    with pytest.raises(expected_error):
        tasks.batch_update_hubspot_objects_chunked(
            HubspotObjectType.CONTACTS.value,
            "user",
            chunk,
        )
    for item in chunk:
        mock_sync_contacts.assert_any_call(item[0])


@pytest.mark.parametrize("id_count", [5, 15])
def test_batch_create_hubspot_objects_chunked(mocker, id_count):
    """batch_create_hubspot_objects_chunked should make expected api calls and args"""
    contacts = UserFactory.create_batch(id_count)
    mock_ids = sorted([contact.id for contact in contacts])
    mock_hubspot_api = mocker.patch("hubspot_sync.tasks.HubspotApi")
    mock_hubspot_api.return_value.crm.objects.batch_api.update.return_value = (
        mocker.Mock(
            results=[SimplePublicObjectFactory(id=mock_id) for mock_id in mock_ids]
        )
    )
    expected_batches = 1 if id_count == 5 else 2
    tasks.batch_create_hubspot_objects_chunked(
        HubspotObjectType.CONTACTS.value, "user", mock_ids
    )
    assert (
        mock_hubspot_api.return_value.crm.objects.batch_api.create.call_count
        == expected_batches
    )
    mock_hubspot_api.return_value.crm.objects.batch_api.create.assert_any_call(
        HubspotObjectType.CONTACTS.value,
        BatchInputSimplePublicObjectInput(
            inputs=[
                make_contact_sync_message(mock_id)
                for mock_id in mock_ids[0 : min(id_count, 10)]
            ]
        ),
    )


@pytest.mark.parametrize(
    "status, expected_error", [[429, TooManyRequestsException], [500, ApiException]]
)
def test_batch_create_hubspot_objects_chunked_error(mocker, status, expected_error):
    """batch_create_hubspot_objects_chunked raise expected exception"""
    mock_hubspot_api = mocker.patch("hubspot_sync.tasks.HubspotApi")
    mock_hubspot_api.return_value.crm.objects.batch_api.create.side_effect = (
        ApiException(status=status)
    )
    mock_sync_contact = mocker.patch(
        "hubspot_sync.tasks.api.sync_contact_with_hubspot",
        side_effect=(ApiException(status=status)),
    )
    chunk = sorted([user.id for user in UserFactory.create_batch(3)])
    with pytest.raises(expected_error):
        tasks.batch_create_hubspot_objects_chunked(
            HubspotObjectType.CONTACTS.value,
            "user",
            chunk,
        )
    for item in chunk:
        mock_sync_contact.assert_any_call(item)


def test_batch_upsert_associations(settings, mocker, mocked_celery):
    """
    batch_upsert_associations should call batch_upsert_associations_chunked w/correct lists of ids
    """
    mock_assoc_chunked = mocker.patch(
        "hubspot_sync.tasks.batch_upsert_associations_chunked"
    )
    settings.HUBSPOT_MAX_CONCURRENT_TASKS = 4
    application_ids = sorted(
        [app.id for app in BootcampApplicationFactory.create_batch(10)]
    )
    with pytest.raises(TabError):
        batch_upsert_associations.delay()
    mock_assoc_chunked.s.assert_any_call(application_ids[0:3])
    mock_assoc_chunked.s.assert_any_call(application_ids[6:9])
    mock_assoc_chunked.s.assert_any_call([application_ids[9]])
    assert mock_assoc_chunked.s.call_count == 4

    with pytest.raises(TabError):
        batch_upsert_associations.delay(application_ids[3:5])
    mock_assoc_chunked.s.assert_any_call([application_ids[3]])
    mock_assoc_chunked.s.assert_any_call([application_ids[4]])


def test_batch_upsert_associations_chunked(settings, mocker):
    """
    batch_upsert_associations_chunked should make expected API calls
    """
    mock_hubspot_api = mocker.patch("hubspot_sync.tasks.HubspotApi")
    applications = BootcampApplicationFactory.create_batch(5)
    expected_line_associations = [
        PublicAssociation(
            _from=HubspotObjectFactory.create(
                content_type=ContentType.objects.get_for_model(app.line),
                object_id=app.line.id,
                content_object=app.line,
            ).hubspot_id,
            to=HubspotObjectFactory.create(
                content_type=ContentType.objects.get_for_model(app),
                object_id=app.id,
                content_object=app,
            ).hubspot_id,
            type=HubspotAssociationType.LINE_DEAL.value,
        )
        for app in applications
    ]
    expected_contact_associations = [
        PublicAssociation(
            _from=HubspotObject.objects.get(
                content_type=ContentType.objects.get_for_model(app), object_id=app.id
            ).hubspot_id,
            to=HubspotObjectFactory.create(
                content_type=ContentType.objects.get_for_model(app.user),
                object_id=app.user.id,
                content_object=app.user,
            ).hubspot_id,
            type=HubspotAssociationType.DEAL_CONTACT.value,
        )
        for app in applications
    ]
    batch_upsert_associations_chunked.delay([app.id for app in applications])
    mock_hubspot_api.return_value.crm.associations.batch_api.create.assert_any_call(
        HubspotObjectType.LINES.value,
        HubspotObjectType.DEALS.value,
        batch_input_public_association=BatchInputPublicAssociation(
            inputs=expected_line_associations
        ),
    )
    mock_hubspot_api.return_value.crm.associations.batch_api.create.assert_any_call(
        HubspotObjectType.DEALS.value,
        HubspotObjectType.CONTACTS.value,
        batch_input_public_association=BatchInputPublicAssociation(
            inputs=expected_contact_associations
        ),
    )


@pytest.mark.parametrize("mode", ["update", "create"])
def test_sync_failed_contacts(mocker, mode):
    """sync_failed_contacts should try to sync each contact and return a list of failed contact ids"""
    user_ids = sorted(user.id for user in UserFactory.create_batch(4))
    mock_sync = mocker.patch(
        "hubspot_sync.tasks.api.sync_contact_with_hubspot",
        side_effect=[
            mocker.Mock(),
            ApiException(status=500, reason="err"),
            mocker.Mock(),
            ApiException(status=429, reason="tmr"),
        ],
    )
    result = tasks.sync_failed_contacts(user_ids)
    assert mock_sync.call_count == 4
    assert result == [user_ids[1], user_ids[3]]


@pytest.mark.parametrize("for_contacts", [True, False])
@pytest.mark.parametrize("has_errors", [True, False])
def test_handle_failed_batch_chunk(mocker, for_contacts, has_errors):
    """handle_failed_batch_chunk should retry contacts only and log exceptions as appropriate"""
    object_ids = [1, 2, 3, 4]
    expected_sync_result = object_ids if has_errors or not for_contacts else []
    hubspot_type = (
        HubspotObjectType.CONTACTS.value
        if for_contacts
        else HubspotObjectType.DEALS.value
    )
    mock_sync_contacts = mocker.patch(
        "hubspot_sync.tasks.sync_failed_contacts", return_value=expected_sync_result
    )
    mock_log = mocker.patch("hubspot_sync.tasks.log.exception")
    tasks.handle_failed_batch_chunk(object_ids, hubspot_type)
    assert mock_sync_contacts.call_count == (
        1 if hubspot_type == HubspotObjectType.CONTACTS.value else 0
    )
    if has_errors or not for_contacts:
        mock_log.assert_called_once_with(
            "Exception when batch syncing Hubspot ids %s of type %s",
            f"{expected_sync_result}",
            hubspot_type,
        )
