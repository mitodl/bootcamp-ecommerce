"""
Hubspot tasks
"""
import logging
import time
from math import ceil
from typing import List, Tuple

import celery
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from hubspot.crm.associations import BatchInputPublicAssociation, PublicAssociation
from hubspot.crm.objects import ApiException, BatchInputSimplePublicObjectInput
from mitol.common.decorators import single_task
from mitol.common.utils.collections import chunks
from mitol.hubspot_api.api import HubspotApi, HubspotAssociationType, HubspotObjectType
from mitol.hubspot_api.decorators import raise_429
from mitol.hubspot_api.exceptions import TooManyRequestsException
from mitol.hubspot_api.models import HubspotObject

from applications.models import BootcampApplication
from hubspot_sync import api
from hubspot_sync.api import get_hubspot_id_for_object
from main.celery import app

log = logging.getLogger(__name__)


def task_obj_lock(
    func_name: str, args: List[object], kwargs: dict  # pylint:disable=unused-argument
) -> str:
    """
    Determine a task lock name for a specific task function and object id

    Args:
        func_name(str): Name of a task function
        args: Task function arguments, first should be object id
        kwargs: Any keyword arguments sent to the task function

    Returns:
        str: The lock id for the task and object
    """
    return f"{func_name}_{args[0]}"


def max_concurrent_chunk_size(obj_count: int) -> int:
    """
    Divide number of objects by max concurrent tasks for chunk size

    Args:
        obj_count: Number of objects

    Returns:
        int: chunk size to use
    """
    return ceil(obj_count / settings.HUBSPOT_MAX_CONCURRENT_TASKS)


def batched_chunks(
    hubspot_type: str, batch_ids: List[int or (int, str)]
) -> List[List[int or str]]:
    """
    If list of ids exceed max allowed in a batch API call, chunk them up

    Args:
        hubspot_type(str): The type of hubspot object (deal, contact, etc)
        batch_ids(list): The list of object ids/emails to process

    Returns:
        list(list): List of chunked ids
    """
    max_chunk_size = 10 if hubspot_type == api.HubspotObjectType.CONTACTS.value else 100
    if len(batch_ids) <= max_chunk_size:
        return [batch_ids]
    return chunks(batch_ids, chunk_size=max_chunk_size)


def sync_failed_contacts(chunk: list[int]) -> list[int]:
    """
    Consecutively try individual contact syncs for a failed batch sync
    Args:
        chunk[list]: list of user id's

    Returns:
        list of contact ids that still failed
    """
    failed_ids = []
    for user_id in chunk:
        try:
            api.sync_contact_with_hubspot(user_id)
            time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
        except ApiException:
            failed_ids.append(user_id)
    return failed_ids


def handle_failed_batch_chunk(chunk: list[int], hubspot_type: str) -> list[int]:
    """
    Try reprocessing a chunk of contacts individually, in case conflicting emails are the problem

    Args:
        chunk [list]: list of object ids
        hubspot_type: The type of Hubspot object

    Returns:
        list of still failing object ids

    """
    failed = chunk
    if hubspot_type == HubspotObjectType.CONTACTS.value:
        # Might be due to conflicting emails, try updating individually
        failed = sync_failed_contacts(chunk)
    if failed:
        log.exception(
            "Exception when batch syncing Hubspot ids %s of type %s",
            f"{failed}",
            hubspot_type,
        )
    return failed


@app.task(
    acks_late=True,
    autoretry_for=(BlockingIOError, TooManyRequestsException),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
@single_task(10, key=task_obj_lock, cache_name="default")
def sync_contact_with_hubspot(user_id: int) -> str:
    """
    Sync a user with a hubspot contact

    Args:
        user_id(int): The User id

    Returns:
        str: The hubspot id for the contact
    """
    return api.sync_contact_with_hubspot(user_id).id


@app.task(
    acks_late=True,
    autoretry_for=(BlockingIOError, TooManyRequestsException),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
@single_task(10, key=task_obj_lock, cache_name="default")
def sync_product_with_hubspot(bootcamp_run_id: int) -> str:
    """
    Sync a product with a hubspot product

    Args:
        bootcamp_run_id(int): The BootcampRun id

    Returns:
        str: The hubspot id for the product
    """
    return api.sync_product_with_hubspot(bootcamp_run_id).id


@app.task(
    acks_late=True,
    autoretry_for=(BlockingIOError, TooManyRequestsException),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
@single_task(10, key=task_obj_lock, cache_name="default")
def sync_deal_with_hubspot(application_id: int) -> str:
    """
    Sync an Order with a hubspot deal

    Args:
        application_id(int): The Order id

    Returns:
        str: The hubspot id for the deal
    """
    return api.sync_deal_with_hubspot(application_id).id


@app.task(
    acks_late=True,
    autoretry_for=(TooManyRequestsException,),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
def batch_create_hubspot_objects_chunked(
    hubspot_type: str, ct_model_name: str, object_ids: List[int]
) -> List[str]:
    """
    Batch create or update a list of hubspot objects, no associations

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        ct_model_name(str): The corresponding bootcamps model name
        object_ids: List of object ids to process

    Returns:
          list(str): list of processed hubspot ids
    """
    created_ids = []
    # Chunk again, by max allowed for object type (10 for contacts, 100 for all else)
    chunked_ids = batched_chunks(hubspot_type, object_ids)
    errored_chunks = []
    last_error_status = None
    for chunk in chunked_ids:
        try:
            response = HubspotApi().crm.objects.batch_api.create(
                hubspot_type,
                BatchInputSimplePublicObjectInput(
                    inputs=[
                        api.MODEL_FUNCTION_MAPPING[ct_model_name](obj_id)
                        for obj_id in chunk
                    ]
                ),
            )
            for result in response.results:
                if ct_model_name == "user":
                    object_id = (
                        User.objects.filter(
                            email__iexact=result.properties["email"], is_active=True
                        )
                        .first()
                        .id
                    )
                else:
                    object_id = result.properties["unique_app_id"].split("-")[-1]
                HubspotObject.objects.update_or_create(
                    content_type=ContentType.objects.get(model=ct_model_name),
                    hubspot_id=result.id,
                    object_id=object_id,
                )
                created_ids.append(result.id)
        except ApiException as ae:
            last_error_status = ae.status
            still_failed = handle_failed_batch_chunk(chunk, hubspot_type)
            if still_failed:
                errored_chunks.append(still_failed)
        time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
    if errored_chunks:
        raise ApiException(
            status=last_error_status,
            reason=f"Batch hubspot create failed for the following chunks: {errored_chunks}",
        )
    return created_ids


@app.task(
    acks_late=True,
    autoretry_for=(TooManyRequestsException,),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
def batch_update_hubspot_objects_chunked(
    hubspot_type: str, ct_model_name: str, object_ids: List[Tuple[int, str]]
) -> List[str]:
    """
    Batch create or update hubspot objects, no associations

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        ct_model_name(str): The corresponding bootcamps model name
        object_ids: List of (object id, hubspot id) tuples to process

    Returns:
          list(str): list of processed hubspot ids
    """
    updated_ids = []
    # Chunk again, by max allowed for object type (10 for contacts, 100 for all else)
    chunked_ids = batched_chunks(hubspot_type, object_ids)
    errored_chunks = []
    last_error_status = None
    for chunk in chunked_ids:
        try:
            inputs = [
                {
                    "id": obj_id[1],
                    "properties": api.MODEL_FUNCTION_MAPPING[ct_model_name](
                        obj_id[0]
                    ).properties,
                }
                for obj_id in chunk
            ]
            response = HubspotApi().crm.objects.batch_api.update(
                hubspot_type, BatchInputSimplePublicObjectInput(inputs=inputs)
            )
            updated_ids.extend([result.id for result in response.results])
        except ApiException as ae:
            last_error_status = ae.status
            still_failed = handle_failed_batch_chunk(
                [item[0] for item in chunk], hubspot_type
            )
            if still_failed:
                errored_chunks.append(still_failed)
        time.sleep(settings.HUBSPOT_TASK_DELAY / 1000)
    if errored_chunks:
        raise ApiException(
            status=last_error_status,
            reason=f"Batch hubspot update failed for the following chunks: {errored_chunks}",
        )
    return updated_ids


@app.task(bind=True)
def batch_upsert_hubspot_objects(  # pylint:disable=too-many-arguments
    self,
    hubspot_type: str,
    model_name: str,
    app_label: str,
    create: bool = True,
    object_ids: List[int] = None,
):
    """
    Batch create or update objects in hubspot, no associations (so ideal for contacts and products)

    Args:
        hubspot_type(str): The hubspot object type (deal, contact, etc)
        model_name(str): The corresponding bootcamps model name
        app_label(str): The model's containing app
        create(bool): Create if true, update if false
        object_ids(list): List of specific object ids to process if any
    """
    content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
    if not object_ids:
        synced_object_ids = HubspotObject.objects.filter(
            content_type=content_type
        ).values_list("object_id", "hubspot_id")
        unsynced_objects = content_type.model_class().objects.exclude(
            id__in=[id[0] for id in synced_object_ids]
        )
        if model_name == "user":
            unsynced_objects = unsynced_objects.filter(
                is_active=True, email__contains="@"
            ).exclude(social_auth__isnull=True)
        unsynced_object_ids = unsynced_objects.values_list("id", flat=True)
        object_ids = unsynced_object_ids if create else synced_object_ids
    elif not create:
        object_ids = HubspotObject.objects.filter(
            content_type=content_type, object_id__in=object_ids
        ).values_list("object_id", "hubspot_id")
    # Limit number of chunks to avoid rate limit
    chunk_size = max_concurrent_chunk_size(len(object_ids))
    chunk_func = (
        batch_create_hubspot_objects_chunked
        if create
        else batch_update_hubspot_objects_chunked
    )
    chunked_tasks = [
        chunk_func.s(hubspot_type, model_name, chunk)
        for chunk in chunks(sorted(object_ids), chunk_size=chunk_size)
    ]
    raise self.replace(celery.group(chunked_tasks))


@app.task(
    acks_late=True,
    autoretry_for=(TooManyRequestsException,),
    max_retries=3,
    retry_backoff=60,
    retry_jitter=True,
)
@raise_429
def batch_upsert_associations_chunked(application_ids: List[int]):
    """
    Upsert batches of deal-contact and line-deal associations

    Args:
        application_ids(list): List of BootcampApplication IDs
    """
    contact_associations_batch = []
    line_associations_batch = []
    hubspot_client = HubspotApi()
    deal_count = len(application_ids)
    for idx, application_id in enumerate(application_ids):
        deal = BootcampApplication.objects.get(id=application_id)
        contact_id = get_hubspot_id_for_object(deal.user)
        deal_id = get_hubspot_id_for_object(deal)
        line_id = get_hubspot_id_for_object(deal.line)
        if contact_id and deal_id:
            contact_associations_batch.append(
                PublicAssociation(
                    _from=deal_id,
                    to=contact_id,
                    type=HubspotAssociationType.DEAL_CONTACT.value,
                )
            )
        if line_id and deal_id:
            line_associations_batch.append(
                PublicAssociation(
                    _from=line_id,
                    to=deal_id,
                    type=HubspotAssociationType.LINE_DEAL.value,
                )
            )
        if (
            len(contact_associations_batch) == 100
            or len(line_associations_batch) == 100
            or idx == deal_count - 1
        ):
            hubspot_client.crm.associations.batch_api.create(
                HubspotObjectType.LINES.value,
                HubspotObjectType.DEALS.value,
                batch_input_public_association=BatchInputPublicAssociation(
                    inputs=line_associations_batch
                ),
            )
            line_associations_batch = []
            hubspot_client.crm.associations.batch_api.create(
                HubspotObjectType.DEALS.value,
                HubspotObjectType.CONTACTS.value,
                batch_input_public_association=BatchInputPublicAssociation(
                    inputs=contact_associations_batch
                ),
            )
            contact_associations_batch = []
    return application_ids


@app.task(bind=True)
def batch_upsert_associations(self, application_ids: List[int] = None):
    """
    Upsert chunked batches of deal-contact and line-deal associations

    Args:
        application_ids(list): List of BootcampApplication IDs
    """
    deals = BootcampApplication.objects.all()
    if application_ids:
        deals = deals.filter(id__in=application_ids)
    chunk_size = max_concurrent_chunk_size(len(deals))
    chunked_tasks = [
        batch_upsert_associations_chunked.s(chunk)
        for chunk in chunks(
            deals.values_list("id", flat=True).order_by("id"), chunk_size=chunk_size
        )
    ]
    raise self.replace(celery.group(chunked_tasks))
