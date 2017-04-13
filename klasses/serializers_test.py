"""
Tests for serializers
"""
import pytest

from klasses.factories import InstallmentFactory
from klasses.serializers import InstallmentSerializer

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


def test_installment_serializer():
    """
    Test for the InstallmentSerializer
    """
    inst = InstallmentFactory.create()

    expected = {
        'installment_number': inst.installment_number,
        'amount': str(inst.amount),
        'deadline': inst.deadline.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    assert InstallmentSerializer(inst).data == expected
