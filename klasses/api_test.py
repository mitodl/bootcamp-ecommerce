"""
klasses API tests
"""

import pytest

from klasses.api import deactivate_run_enrollment
from klasses.constants import ENROLL_CHANGE_STATUS_REFUNDED
from klasses.factories import BootcampRunEnrollmentFactory


pytestmark = pytest.mark.django_db


def test_deactivate_run_enrollment():
    """ Test that deactivate_run_enrollment updates enrollment fields correctly"""
    enrollment = BootcampRunEnrollmentFactory.create()
    deactivate_run_enrollment(enrollment, ENROLL_CHANGE_STATUS_REFUNDED)
    assert enrollment.active is False
    assert enrollment.change_status == ENROLL_CHANGE_STATUS_REFUNDED
