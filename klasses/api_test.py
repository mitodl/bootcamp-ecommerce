"""
Tests for api module
"""
from decimal import Decimal
from unittest.mock import PropertyMock

import pytest

from ecommerce.factories import OrderFactory, LineFactory
from ecommerce.models import Order, Line
from ecommerce.serializers import LineSerializer
from fluidreview.constants import WebhookParseStatus
from fluidreview.factories import WebhookRequestFactory
from klasses.api import (
    serialize_user_bootcamp_run,
    serialize_user_bootcamp_runs,
)
from klasses.bootcamp_admissions_client import BootcampAdmissionClient
from klasses.factories import BootcampRunFactory, InstallmentFactory
from klasses.serializers import InstallmentSerializer
from profiles.factories import ProfileFactory

# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


@pytest.fixture()
def test_data(mocker):
    """
    Sets up the data for all the tests in this module
    """
    profile = ProfileFactory.create()
    run_paid = BootcampRunFactory.create()
    run_not_paid = BootcampRunFactory.create()
    WebhookRequestFactory(
        award_id=run_paid.run_key,
        user_email=profile.user.email,
        user_id=profile.fluidreview_id,
        status=WebhookParseStatus.SUCCEEDED)
    WebhookRequestFactory(
        award_id=run_not_paid.run_key,
        user_email=profile.user.email,
        user_id=profile.fluidreview_id,
        status=WebhookParseStatus.SUCCEEDED)

    InstallmentFactory.create(bootcamp_run=run_paid)
    InstallmentFactory.create(bootcamp_run=run_not_paid)

    order = OrderFactory.create(user=profile.user, status=Order.FULFILLED)
    LineFactory.create(order=order, run_key=run_paid.run_key, price=627.34)

    return profile.user, run_paid, run_not_paid


def test_serialize_user_bootcamp_run_bootclient_equivalent(test_data):
    """
    Test for serialize_user_bootcamp_run to verify that passing or not passing the bootcamp client is equivalent.
    """
    user, run_paid, _ = test_data

    assert serialize_user_bootcamp_run(user, run_paid) == serialize_user_bootcamp_run(
        user, run_paid, BootcampAdmissionClient(user))


def test_serialize_user_run_paid(test_data):
    """
    Test for serialize_user_bootcamp_run for a paid bootcamp run
    """
    user, run_paid, _ = test_data

    expected_ret = {
        "run_key": run_paid.run_key,
        "bootcamp_run_name": run_paid.title,
        "display_title": run_paid.display_title,
        "start_date": run_paid.start_date,
        "end_date": run_paid.end_date,
        "price": run_paid.personal_price(user),
        "is_user_eligible_to_pay": True,
        "total_paid": Decimal('627.34'),
        "payments": LineSerializer(Line.for_user_bootcamp_run(user, run_paid.run_key), many=True).data,
        "installments": InstallmentSerializer(
            run_paid.installment_set.order_by('deadline'), many=True).data,
    }
    assert expected_ret == serialize_user_bootcamp_run(user, run_paid)


def test_serialize_user_run_not_paid(test_data):
    """
    Test for serialize_user_bootcamp_run for a not paid bootcamp run
    """
    user, _, run_not_paid = test_data

    expected_ret = {
        "run_key": run_not_paid.run_key,
        "bootcamp_run_name": run_not_paid.title,
        "display_title": run_not_paid.display_title,
        "start_date": run_not_paid.start_date,
        "end_date": run_not_paid.end_date,
        "price": run_not_paid.personal_price(user),
        "is_user_eligible_to_pay": True,
        "total_paid": Decimal('0.00'),
        "payments": [],
        "installments": InstallmentSerializer(
            run_not_paid.installment_set.order_by('deadline'), many=True).data,
    }
    assert expected_ret == serialize_user_bootcamp_run(user, run_not_paid)


def test_serialize_user_bootcamp_runs(test_data):
    """
    Test for serialize_user_bootcamp_runs in normal case
    """
    user, run_paid, run_not_paid = test_data
    expected_ret = [
        {
            "run_key": run_paid.run_key,
            "bootcamp_run_name": run_paid.title,
            "display_title": run_paid.display_title,
            "start_date": run_paid.start_date,
            "end_date": run_paid.end_date,
            "price": run_paid.price,
            "is_user_eligible_to_pay": True,
            "total_paid": Decimal('627.34'),
            "payments": LineSerializer(Line.for_user_bootcamp_run(user, run_paid.run_key), many=True).data,
            "installments": InstallmentSerializer(
                run_paid.installment_set.order_by('deadline'), many=True).data,
        },
        {
            "run_key": run_not_paid.run_key,
            "bootcamp_run_name": run_not_paid.title,
            "display_title": run_not_paid.display_title,
            "start_date": run_not_paid.start_date,
            "end_date": run_not_paid.end_date,
            "price": run_not_paid.price,
            "is_user_eligible_to_pay": True,
            "total_paid": Decimal('0.00'),
            "payments": [],
            "installments": InstallmentSerializer(
                run_not_paid.installment_set.order_by('deadline'), many=True).data,
        }
    ]
    assert sorted(expected_ret, key=lambda x: x['run_key']) == serialize_user_bootcamp_runs(user)


def test_serialize_user_bootcamp_runs_paid_not_payable(test_data, mocker):
    """
    Test for serialize_user_bootcamp_runs in case the user is not eligible to pay but she has already paid for the
    bootcamp run
    """
    user, run_paid, run_not_paid = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_bootcamp_run_keys',
        new_callable=PropertyMock,
        return_value=[run_not_paid.run_key],
    )
    res = serialize_user_bootcamp_runs(user)
    assert run_paid.run_key in [bootcamp_run['run_key'] for bootcamp_run in res]
    for bootcamp_run in res:
        if bootcamp_run['run_key'] == run_paid.run_key:
            break
    assert bootcamp_run['is_user_eligible_to_pay'] is False  # pylint: disable=undefined-loop-variable
