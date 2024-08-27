"""
Tests for bootcamp serializers
"""

from datetime import timedelta

import pytest
from mitol.common.utils import now_in_utc

from cms.factories import AdmissionSectionFactory, BootcampRunPageFactory
from cms.serializers import BootcampRunPageSerializer
from klasses.factories import BootcampFactory, BootcampRunFactory, InstallmentFactory
from klasses.serializers import (
    BootcampRunSerializer,
    BootcampSerializer,
    InstallmentSerializer,
)
from main.utils import serializer_date_format

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
        "readable_id": bootcamp.readable_id,
    }


def test_bootcamp_run_serializer():
    """BootcampRunSerializer should serialize the bootcamp run"""
    run = BootcampRunFactory.create(start_date=now_in_utc() + timedelta(days=10))
    installment = InstallmentFactory.create(bootcamp_run=run)
    assert BootcampRunSerializer(run).data == {
        "id": run.id,
        "title": run.title,
        "display_title": run.display_title,
        "bootcamp": BootcampSerializer(run.bootcamp).data,
        "start_date": serializer_date_format(run.start_date),
        "end_date": serializer_date_format(run.end_date),
        "early_bird_deadline": None,
        "run_key": run.run_key,
        "installments": [InstallmentSerializer(installment).data],
        "novoed_course_stub": run.novoed_course_stub,
        "is_payable": True,
        "bootcamp_run_id": run.bootcamp_run_id,
        "allows_skipped_steps": run.allows_skipped_steps,
    }


def test_bootcamp_run_serializer_with_page():
    """BootcampRunSerializer should serialize the bootcamp run with CMS page data if requested in the context"""
    run = BootcampRunFactory.create()
    serialized = BootcampRunSerializer(run, context={"include_page": True}).data
    assert "page" in serialized
    assert serialized["page"] == {}
    page = BootcampRunPageFactory.create(bootcamp_run=run)
    AdmissionSectionFactory.create(
        parent=page,
        admissions_image__title="title of the image",
        notes="notes",
        details="details",
        bootcamp_location="bootcamp format",
        bootcamp_location_details="format details",
        dates="dates",
        dates_details="dates details",
        price=10,
        price_details="price details",
    )
    serialized = BootcampRunSerializer(run, context={"include_page": True}).data
    assert serialized["page"] == BootcampRunPageSerializer(instance=page).data
