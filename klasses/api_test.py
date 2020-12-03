"""
klasses API tests
"""
import datetime

import pytest
import pytz

from klasses.api import deactivate_run_enrollment, fetch_bootcamp_run
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.factories import BootcampRunEnrollmentFactory
from klasses.factories import BootcampRunFactory
from klasses.models import BootcampRun

pytestmark = pytest.mark.django_db


def test_deactivate_run_enrollment():
    """Test that deactivate_run_enrollment updates enrollment fields correctly"""
    enrollment = BootcampRunEnrollmentFactory.create()
    deactivate_run_enrollment(enrollment, ENROLL_CHANGE_STATUS_REFUNDED)
    assert enrollment.active is False
    assert enrollment.change_status == ENROLL_CHANGE_STATUS_REFUNDED


@pytest.mark.django_db
def test_fetch_bootcamp_run():
    """fetch_bootcamp_run should fetch a bootcamp run with a field value that matches the given property"""
    run = BootcampRunFactory.create(
        bootcamp__title="Bootcamp 1", title="Run 1", start_date=None, end_date=None
    )
    assert fetch_bootcamp_run(str(run.id)) == run
    assert fetch_bootcamp_run(run.title) == run
    assert fetch_bootcamp_run(run.display_title) == run
    with pytest.raises(BootcampRun.DoesNotExist):
        fetch_bootcamp_run("invalid")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "end_date_params",
    [
        dict(year=2020, month=1, day=15),
        dict(year=2020, month=2, day=1),
        dict(year=2021, month=1, day=1),
        None,
    ],
)
def test_fetch_bootcamp_run_dates(end_date_params):
    """fetch_bootcamp_run should fetch a bootcamp run by display title regardless of the start/end date ranges"""
    run = BootcampRunFactory.create(
        bootcamp__title="Bootcamp 1",
        title="Run 1",
        start_date=datetime.datetime(year=2020, month=1, day=1, tzinfo=pytz.UTC),
        end_date=(
            None
            if not end_date_params
            else datetime.datetime(**end_date_params, tzinfo=pytz.UTC)
        ),
    )
    assert fetch_bootcamp_run(run.display_title) == run
    with pytest.raises(BootcampRun.DoesNotExist):
        fetch_bootcamp_run("invalid")
