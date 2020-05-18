"""
Tests for serializers
"""
import pytest

from klasses.factories import BootcampFactory, BootcampRunFactory, InstallmentFactory
from klasses.serializers import BootcampSerializer, BootcampRunSerializer, InstallmentSerializer
from main.test_utils import serializer_date_format

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


def test_installment_serializer():
    """
    Test for the InstallmentSerializer
    """
    inst = InstallmentFactory.create()

    expected = {
        'amount': inst.amount,
        'deadline': inst.deadline.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    assert InstallmentSerializer(inst).data == expected


def test_bootcamp_serializer():
    """BootcampSerializer should serialize basic Bootcamp information"""
    bootcamp = BootcampFactory.create()
    assert BootcampSerializer(bootcamp).data == {
        "title": bootcamp.title,
        "id": bootcamp.id,
    }


def test_bootcamp_run_serializer():
    """BootcampRunSerializer should serialize the bootcamp run"""
    run = BootcampRunFactory.create()
    assert BootcampRunSerializer(run).data == {
        "id": run.id,
        "title": run.title,
        "display_title": run.display_title,
        "bootcamp": BootcampSerializer(run.bootcamp).data,
        "start_date": serializer_date_format(run.start_date),
        "end_date": serializer_date_format(run.end_date),
        "run_key": run.run_key,
    }
