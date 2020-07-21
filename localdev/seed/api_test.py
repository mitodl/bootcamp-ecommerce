"""Seed data API tests"""
# pylint: disable=unused-argument, redefined-outer-name
from types import SimpleNamespace
import pytest

from klasses.models import Bootcamp, BootcampRun
from applications.models import ApplicationStep, BootcampRunApplicationStep
from localdev.seed.config import SEED_DATA_PREFIX
from localdev.seed.utils import get_raw_seed_data_from_file, seed_prefixed
from localdev.seed.api import create_seed_data, delete_seed_data


@pytest.fixture
def seeded():
    """Fixture for a scenario where seed data has been loaded from our JSON file"""
    data = get_raw_seed_data_from_file()
    create_seed_data(data)
    return SimpleNamespace(raw_data=data)


@pytest.mark.django_db
def test_seed_prefix(seeded):  # pylint: disable=unused-argument
    """
    A prefix should be added to certain field values that indicates which objects are seed data
    """
    # Test helper function(s)
    assert seed_prefixed("Some Title") == "{}Some Title".format(SEED_DATA_PREFIX)
    # Test saved object titles
    assert (
        Bootcamp.objects.exclude(title__startswith=SEED_DATA_PREFIX).exists() is False
    )
    assert (
        BootcampRun.objects.exclude(title__startswith=SEED_DATA_PREFIX).exists()
        is False
    )


@pytest.mark.django_db
def test_seed_and_unseed_data(seeded):
    """Tests that the seed data functions can create and delete seed data"""
    bootcamps_data = seeded.raw_data["bootcamps"]
    expected_bootcamp_count = len(bootcamps_data)
    expected_runs_count = sum(
        len(bootcamp_data.get("[runs]", [])) for bootcamp_data in bootcamps_data
    )
    expected_steps_count = sum(
        len(bootcamp_data.get("[steps]", [])) for bootcamp_data in bootcamps_data
    )
    expected_run_step_count = sum(
        len(bootcamp_data.get("[steps]", [])) * len(bootcamp_data.get("[runs]", []))
        for bootcamp_data in bootcamps_data
    )
    db_bootcamp_count = Bootcamp.objects.count()
    db_run_count = BootcampRun.objects.count()
    db_step_count = ApplicationStep.objects.count()
    db_run_step_count = BootcampRunApplicationStep.objects.count()
    assert db_bootcamp_count == expected_bootcamp_count
    assert db_run_count == expected_runs_count
    assert db_step_count == expected_steps_count
    assert db_run_step_count == expected_run_step_count

    delete_seed_data(seeded.raw_data)
    assert Bootcamp.objects.count() == 0
    assert BootcampRun.objects.count() == 0
    assert ApplicationStep.objects.count() == 0
    assert BootcampRunApplicationStep.objects.count() == 0
