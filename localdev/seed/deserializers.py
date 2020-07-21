"""
Seed data deserializers
"""
from datetime import timedelta

from django.db.models import Max

from applications.models import ApplicationStep, BootcampRunApplicationStep
from klasses.models import Bootcamp, BootcampRun, Installment
from localdev.seed.config import DateRangeOption
from localdev.seed.utils import (
    get_date_range,
    parse_date_range_choice,
    seed_adjusted_field_data,
    set_model_properties_from_dict,
)

INSTALLMENT_DUE_DATE_OFFSET_DAYS = 5
RUN_APP_STEP_DUE_DATE_OFFSET_DAYS = 5


def deserialize_bootcamp(seed_data_spec):
    """
    Creates/updates/fetches a Bootcamp described by seed data

    Args:
        seed_data_spec (loclocaldev/seed/deserializers.pyaldev.seed.utils.SeedDataSpec): The seed data specification

    Returns:
        Tuple[Bootcamp, bool, bool]: The Bootcamp database object, a flag indicating whether or not
            it was newly created, and a flag indicating whether or not it was updated
    """
    field_data = seed_adjusted_field_data(
        seed_data_spec.model_cls, seed_data_spec.raw_item_data
    )
    existing_obj_qset = Bootcamp.objects.filter(**field_data)
    if existing_obj_qset.exists():
        return existing_obj_qset.first(), False, False
    bootcamp = Bootcamp.objects.create(**field_data)
    return bootcamp, True, False


def deserialize_bootcamp_run(seed_data_spec):
    """
    Creates/updates/fetches a BootcampRun described by seed data

    Args:
        seed_data_spec (localdev.seed.utils.SeedDataSpec): The seed data specification

    Returns:
        Tuple[BootcampRun, bool, bool]: The BootcampRun database object, a flag indicating whether or not
            it was newly created, and a flag indicating whether or not it was updated
    """
    if seed_data_spec.parent_spec.db_object is None:
        raise ValueError("BootcampRun requires a parent Bootcamp")
    field_data = seed_adjusted_field_data(
        seed_data_spec.model_cls, seed_data_spec.raw_item_data
    )
    date_range_choice = parse_date_range_choice(seed_data_spec.raw_item_data)
    date_index = 0
    if date_range_choice == DateRangeOption.future.value:
        # If any previous siblings are also set to be in the future, set an index value to indicate which one
        # this is in the series
        date_index = len(
            [
                item
                for item in seed_data_spec.prev_sibling_data
                if parse_date_range_choice(item) == date_range_choice
            ]
        )
    elif date_range_choice == DateRangeOption.past.value:
        # If any future siblings are also set to be in the past, set an index value to indicate which one
        # this is in the series
        date_index = len(
            [
                item
                for item in seed_data_spec.next_sibling_data
                if parse_date_range_choice(item) == date_range_choice
            ]
        )
    start_date, end_date = get_date_range(
        date_range_choice=date_range_choice, series_index=date_index
    )
    query_dict = dict(**field_data, bootcamp=seed_data_spec.parent_spec.db_object)
    upsert_dict = dict(start_date=start_date, end_date=end_date)
    existing_obj_qset = BootcampRun.objects.filter(**query_dict)
    if existing_obj_qset.exists():
        existing_obj = existing_obj_qset.first()
        updated_obj = set_model_properties_from_dict(existing_obj, upsert_dict)
        return updated_obj, False, True
    max_run_key = (
        BootcampRun.objects.aggregate(max_run_key=Max("run_key"))["max_run_key"] or 0
    )
    bootcamp_run = BootcampRun.objects.create(
        **query_dict, **upsert_dict, run_key=max_run_key + 1
    )
    return bootcamp_run, True, False


def deserialize_app_step(seed_data_spec):
    """
    Creates/updates/fetches an ApplicationStep described by seed data

    Args:
        seed_data_spec (localdev.seed.utils.SeedDataSpec): The seed data specification

    Returns:
        Tuple[ApplicationStep, bool, bool]: The ApplicationStep database object, a flag indicating whether or not
            it was newly created, and a flag indicating whether or not it was updated
    """
    if seed_data_spec.parent_spec.db_object is None:
        raise ValueError("ApplicationStep requires a parent Bootcamp")
    if "submission_type" not in seed_data_spec.raw_item_data:
        raise ValueError("ApplicationStep needs a 'submission_type' value")
    submission_type = seed_data_spec.raw_item_data["submission_type"]
    query_dict = dict(
        step_order=seed_data_spec.index, bootcamp=seed_data_spec.parent_spec.db_object
    )
    existing_obj_qset = ApplicationStep.objects.filter(**query_dict)
    if existing_obj_qset.exists():
        app_step = existing_obj_qset.first()
        if app_step.submission_type != submission_type:
            app_step.submission_type = submission_type
            app_step.save()
            return app_step, False, True
        return app_step, False, False
    app_step = ApplicationStep.objects.create(
        **query_dict, submission_type=submission_type
    )
    return app_step, True, False


def deserialize_installment(seed_data_spec):
    """
    Creates/updates/fetches an Installment described by seed data

    Args:
        seed_data_spec (localdev.seed.utils.SeedDataSpec): The seed data specification

    Returns:
        Tuple[Installment, bool, bool]: The Installment database object, a flag indicating whether or not
            it was newly created, and a flag indicating whether or not it was updated
    """
    if seed_data_spec.parent_spec.db_object is None:
        raise ValueError("Installment requires a parent BootcampRun")
    if "amount" not in seed_data_spec.raw_item_data:
        raise ValueError("Installment needs an 'amount' value")
    amount = seed_data_spec.raw_item_data["amount"]
    parent_bootcamp_run = seed_data_spec.parent_spec.db_object
    deadline_offset = INSTALLMENT_DUE_DATE_OFFSET_DAYS * (seed_data_spec.index + 1)
    deadline = parent_bootcamp_run.start_date - timedelta(days=deadline_offset)
    existing_installments = Installment.objects.filter(
        bootcamp_run=parent_bootcamp_run
    ).order_by("deadline", "id")
    if seed_data_spec.index < len(existing_installments):
        existing_installment = existing_installments[seed_data_spec.index]
        if (
            existing_installment.amount == amount
            and existing_installment.deadline == deadline
        ):
            return existing_installment, False, False
        installment = set_model_properties_from_dict(
            existing_installment, dict(amount=amount, deadline=deadline)
        )
        return installment, False, True
    installment = Installment.objects.create(
        bootcamp_run=parent_bootcamp_run, amount=amount, deadline=deadline
    )
    return installment, True, False


def deserialize_run_app_step(seed_data_spec):
    """
    Creates/updates/fetches an BootcampRunApplicationStep described by seed data

    Args:
        seed_data_spec (localdev.seed.utils.SeedDataSpec): The seed data specification

    Returns:
        Tuple[BootcampRunApplicationStep, bool, bool]: The BootcampRunApplicationStep database object,
            a flag indicating whether or not it was newly created, and a flag indicating whether or not
            it was updated
    """
    if seed_data_spec.parent_spec.db_object is None:
        raise ValueError("BootcampRunApplicationStep requires a parent BootcampRun")
    parent_bootcamp_run = seed_data_spec.parent_spec.db_object
    app_steps = ApplicationStep.objects.filter(
        bootcamp=parent_bootcamp_run.bootcamp
    ).order_by("step_order")
    num_app_steps = len(app_steps)
    target_app_step = app_steps[seed_data_spec.index]
    #
    run_app_steps = BootcampRunApplicationStep.objects.filter(
        bootcamp_run=parent_bootcamp_run
    ).order_by("due_date")
    due_date_offset = RUN_APP_STEP_DUE_DATE_OFFSET_DAYS * (
        num_app_steps - seed_data_spec.index
    )
    due_date = parent_bootcamp_run.start_date - timedelta(days=due_date_offset)
    if seed_data_spec.index < len(run_app_steps):
        existing_run_app_step = run_app_steps[seed_data_spec.index]
        if (
            existing_run_app_step.due_date == due_date
            and existing_run_app_step.application_step == target_app_step
        ):
            return existing_run_app_step, False, False
        existing_run_app_step.due_date = due_date
        existing_run_app_step.application_step = target_app_step
        existing_run_app_step.save()
        return existing_run_app_step, False, True
    new_app_step = BootcampRunApplicationStep.objects.create(
        bootcamp_run=parent_bootcamp_run,
        application_step=target_app_step,
        due_date=due_date,
    )
    return new_app_step, True, False


MODEL_SERIALIZER_MAP = {
    Bootcamp: deserialize_bootcamp,
    BootcampRun: deserialize_bootcamp_run,
    ApplicationStep: deserialize_app_step,
    Installment: deserialize_installment,
    BootcampRunApplicationStep: deserialize_run_app_step,
}
