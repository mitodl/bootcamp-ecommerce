"""
Tests for bootcamp serializers
"""
import pytest

from cms.factories import BootcampRunPageFactory
from cms.serializers import BootcampRunPageSerializer
from klasses.factories import BootcampFactory, BootcampRunFactory, InstallmentFactory
from klasses.serializers import (
    BootcampSerializer,
    BootcampRunSerializer,
    InstallmentSerializer,
)
from main.utils import serializer_date_format

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


def test_installment_serializer():
    """
    Test for the InstallmentSerializer
    """
    inst = InstallmentFactory.create()

    expected = {
        "amount": inst.amount,
        "deadline": inst.deadline.strftime("%Y-%m-%dT%H:%M:%SZ"),
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
    installment = InstallmentFactory.create(bootcamp_run=run)
    assert BootcampRunSerializer(run).data == {
        "id": run.id,
        "title": run.title,
        "display_title": run.display_title,
        "bootcamp": BootcampSerializer(run.bootcamp).data,
        "start_date": serializer_date_format(run.start_date),
        "end_date": serializer_date_format(run.end_date),
        "run_key": run.run_key,
        "installments": [InstallmentSerializer(installment).data],
    }


def test_bootcamp_run_serializer_with_page():
    """BootcampRunSerializer should serialize the bootcamp run with CMS page data if requested in the context"""
    run = BootcampRunFactory.create()
    serialized = BootcampRunSerializer(run, context={"include_page": True}).data
    assert "page" in serialized
    assert serialized["page"] == {}
    page = BootcampRunPageFactory.create(bootcamp_run=run)
    serialized = BootcampRunSerializer(run, context={"include_page": True}).data
    assert serialized["page"] == BootcampRunPageSerializer(instance=page).data
