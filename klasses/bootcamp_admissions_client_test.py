"""
Tests for the bootcamp_admission_client module
"""
import pytest

from fluidreview.constants import WebhookParseStatus
from smapply.factories import WebhookRequestSMAFactory
from klasses.bootcamp_admissions_client import (
    BootcampAdmissionClient,
)
from profiles.factories import ProfileFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


def test_can_pay_klass():
    """
    Test BootcampAdmissionClient.can_pay_klass with smapply klasses
    """
    profile = ProfileFactory.create(user__email="foo@example.com", fluidreview_id=9999, smapply_id=8888)
    user = profile.user
    smapply_klass = 19
    WebhookRequestSMAFactory(
        award_id=smapply_klass,
        user_id=user.profile.smapply_id,
        status=WebhookParseStatus.SUCCEEDED)

    boot_client = BootcampAdmissionClient(user)
    assert boot_client.can_pay_klass(smapply_klass) is True
    assert boot_client.can_pay_klass('foo') is False
