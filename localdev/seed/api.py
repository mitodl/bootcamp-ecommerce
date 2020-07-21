"""Data seeding API"""
import json
from collections import defaultdict

from applications.models import ApplicationStep, BootcampRunApplicationStep
from klasses.models import Bootcamp, BootcampRun, Installment
from localdev.seed.utils import (
    SeedDataSpec,
    get_child_object_data,
    get_own_data,
    seed_adjusted_field_data,
)
from localdev.seed.deserializers import MODEL_SERIALIZER_MAP
from main.utils import partition_around_index


class SeedResult:
    """Represents the results of seeding/unseeding"""

    def __init__(self):
        self.created = defaultdict(int)
        self.updated = defaultdict(int)
        self.deleted = defaultdict(int)
        self.ignored = defaultdict(int)
        self.invalid = defaultdict(dict)

    def add_created(self, obj):
        """Adds to the count of created object types"""
        self.created[obj.__class__.__name__] += 1

    def add_updated(self, obj):
        """Adds to the count of updated object types"""
        self.updated[obj.__class__.__name__] += 1

    def add_ignored(self, obj):
        """Adds to the count of ignored object types"""
        self.ignored[obj.__class__.__name__] += 1

    def add_deleted(self, deleted_type_dict):
        """Adds to the count of deleted object types"""
        for deleted_type, deleted_count in deleted_type_dict.items():
            if deleted_count:
                self.deleted[deleted_type] += deleted_count

    def add_invalid(self, model_cls, index, raw_data, exc):
        """
        Adds debugging messages for objects that failed to save for any reason

        Args:
            model_cls (Type(django.db.models.base.Model)): The model class
            index (int): The index of this seed data item in the raw data
            raw_data (dict): Raw seed data that describes the object
            exc (Exception): The exception encountered while trying to save
        """
        joined_values = ",".join(map(str, raw_data.values()))[0:30]
        self.invalid[model_cls.__name__][f"[{index}] {joined_values}"] = str(exc)

    @property
    def has_results(self):
        """Returns True if any results have been logged"""
        return (
            self.created or self.updated or self.deleted or self.ignored or self.invalid
        )

    @property
    def report(self):
        """String representing the seed result"""
        invalid_report = ""
        if self.invalid:
            invalid_data_str = json.dumps(dict(self.invalid), indent=2)
            invalid_report = f"\nInvalid:\n{invalid_data_str}"
        return (
            f"Created: {dict(self.created)}"
            f"\nUpdated: {dict(self.updated)}"
            f"\nDeleted: {dict(self.deleted)}"
            f"\nIgnored (Already Existed): {dict(self.ignored)}"
            f"{invalid_report}"
        )

    def __repr__(self):
        return str(self.report)


def raw_data_list_iterator(raw_data_list, model_cls, parent_spec=None):
    """
    Iterates through a list of raw data of a specific type and yields a seed data spec for each object in the list

    Args:
        raw_data_list (List[dict]): The list of raw seed data
        model_cls (Type[django.db.models.Model]): The model class of the objects being described in this list
        parent_spec (Optional[SeedDataSpec]): The seed data spec of the parent object of this list

    Yields:
        SeedDataSpec: Specification for a model object that should be created/updated/deleted
    """
    for idx, raw_item_data in enumerate(raw_data_list):
        # Get the data of the objects in this list before and after the object that is currently being inspected
        prev_sibling_data, next_sibling_data = partition_around_index(
            raw_data_list, idx
        )
        yield SeedDataSpec(
            model_cls=model_cls,
            # Exclude any child object data when setting the raw item data and sibling data
            raw_item_data=get_own_data(raw_item_data),
            prev_sibling_data=list(map(get_own_data, prev_sibling_data)),
            next_sibling_data=list(map(get_own_data, next_sibling_data)),
            child_object_data=get_child_object_data(raw_item_data),
            parent_spec=parent_spec,
            index=idx,
        )


def iter_seed_data(raw_data):
    """
    Iterate through raw seed data and yields the specification for models that should be created/updated/deleted.

    Yields:
        SeedDataSpec: Specification for a model object that should be created/updated/deleted
    """
    raw_bootcamps_data = raw_data["bootcamps"]
    for bootcamp_spec in raw_data_list_iterator(raw_bootcamps_data, model_cls=Bootcamp):
        yield bootcamp_spec

        app_steps_data = bootcamp_spec.child_object_data.get("[steps]", [])
        for app_step_spec in raw_data_list_iterator(
            app_steps_data, model_cls=ApplicationStep, parent_spec=bootcamp_spec
        ):
            yield app_step_spec

        bootcamp_runs_data = bootcamp_spec.child_object_data.get("[runs]", [])
        for bootcamp_run_spec in raw_data_list_iterator(
            bootcamp_runs_data, model_cls=BootcampRun, parent_spec=bootcamp_spec
        ):
            yield bootcamp_run_spec

            installments_data = bootcamp_run_spec.child_object_data.get(
                "[installments]", []
            )
            for installment_spec in raw_data_list_iterator(
                installments_data, model_cls=Installment, parent_spec=bootcamp_run_spec
            ):
                yield installment_spec

            # Yield a spec for BootcampRunApplicationStep objects that correspond to each
            # ApplicationStep, unless a specific key exists in the bootcamp run data.
            if bootcamp_run_spec.raw_item_data.get("_ignore_run_steps"):
                continue
            for run_step_index in range(len(app_steps_data)):
                yield SeedDataSpec(
                    model_cls=BootcampRunApplicationStep,
                    raw_item_data={},
                    prev_sibling_data=[],
                    next_sibling_data=[],
                    child_object_data={},
                    parent_spec=bootcamp_run_spec,
                    index=run_step_index,
                )


def create_seed_data(raw_data):
    """
    Iterate over all objects described in the seed data, add/update them one-by-one, and return the results

    Args:
        raw_data (List[dict]): Raw data that describes objects that we want to be seeded in the database

    Returns:
        SeedResult: The results of seeding
    """
    seed_result = SeedResult()
    for seed_data_spec in iter_seed_data(raw_data):
        deserializer = MODEL_SERIALIZER_MAP[seed_data_spec.model_cls]
        try:
            db_object, created, updated = deserializer(seed_data_spec)
        except Exception as exc:  # pylint: disable=broad-except
            seed_result.add_invalid(
                seed_data_spec.model_cls,
                index=seed_data_spec.index,
                raw_data=seed_data_spec.raw_item_data,
                exc=exc,
            )
            continue
        seed_data_spec.db_object = db_object
        if created:
            seed_result.add_created(db_object)
        elif updated:
            seed_result.add_updated(db_object)
        else:
            seed_result.add_ignored(db_object)
    return seed_result


def delete_seed_data(raw_data):
    """
    Delete all objects described in the seed data

    Args:
        raw_data (List[dict]): Raw data that describes objects that we want to be unseeded in the database

    Returns:
        SeedResult: The results of unseeding
    """
    seed_result = SeedResult()
    # Deleting all the seeded Bootcamps will delete all of the other seeded objects thanks to cascading deletes.
    bootcamp_specs = [
        seed_data_spec
        for seed_data_spec in iter_seed_data(raw_data)
        if seed_data_spec.model_cls == Bootcamp
    ]
    for bootcamp_spec in bootcamp_specs:
        _, deleted_type_dict = Bootcamp.objects.filter(
            **seed_adjusted_field_data(Bootcamp, bootcamp_spec.raw_item_data)
        ).delete()
        seed_result.add_deleted(deleted_type_dict)
    return seed_result
