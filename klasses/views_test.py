"""
Tests for views
"""
from unittest.mock import PropertyMock

import pytest
from django.urls import reverse
from rest_framework import status

from backends.edxorg import EdxOrgOAuth2
from ecommerce.factories import OrderFactory, LineFactory
from ecommerce.models import Order
from klasses.conftest import patch_get_admissions
from klasses.factories import BootcampRunFactory
from profiles.factories import ProfileFactory


# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


BOOTCAMP_RUN_FIELDS = [
    'run_key',
    'start_date',
    'end_date',
    'total_paid',
    'installments',
    'payments',
    'bootcamp_run_name',
    'display_title',
    'is_user_eligible_to_pay',
    'price',
]


@pytest.fixture()
def test_data(mocker):
    """
    Sets up the data for all the tests in this module
    """
    profile = ProfileFactory.create()
    user = profile.user
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid=user.username,
        extra_data={"access_token": "fooooootoken"}
    )
    other_user = ProfileFactory.create().user

    for _ in range(3):
        bootcamp_run = BootcampRunFactory.create()

    patch_get_admissions(mocker)
    # just need one bootcamp run, so returning the last created
    return user, other_user, bootcamp_run


@pytest.fixture()
def fulfilled_order(test_data):
    user, _, bootcamp_run = test_data
    order = OrderFactory.create(user=user, status=Order.FULFILLED)
    LineFactory.create(order=order, run_key=bootcamp_run.run_key, price=123.45)
    return order


def test_only_self_can_access_apis(test_data, client):
    """
    Only the the requester user can access her own info
    """
    user, other_user, bootcamp_run = test_data
    detail_url_user = reverse('bootcamp-run-detail', kwargs={'username': user.username, 'run_key': bootcamp_run.run_key})
    detail_url_other_user = reverse(
        'bootcamp-run-detail', kwargs={'username': other_user.username, 'run_key': bootcamp_run.run_key})
    list_url_user = reverse('bootcamp-run-list', kwargs={'username': user.username})
    list_url_other_user = reverse('bootcamp-run-list', kwargs={'username': other_user.username})

    # anonymous
    for url in (detail_url_user, detail_url_other_user, list_url_user, list_url_other_user, ):
        assert client.get(url).status_code == status.HTTP_403_FORBIDDEN

    client.force_login(other_user)
    assert client.get(detail_url_user).status_code == status.HTTP_403_FORBIDDEN
    assert client.get(detail_url_other_user).status_code == status.HTTP_404_NOT_FOUND
    assert client.get(list_url_user).status_code == status.HTTP_403_FORBIDDEN
    assert client.get(list_url_other_user).status_code == status.HTTP_404_NOT_FOUND

    client.force_login(user)
    assert client.get(detail_url_user).status_code == status.HTTP_200_OK
    assert client.get(detail_url_other_user).status_code == status.HTTP_404_NOT_FOUND
    assert client.get(list_url_user).status_code == status.HTTP_200_OK
    assert client.get(list_url_other_user).status_code == status.HTTP_404_NOT_FOUND


def test_bootcamp_run_detail(test_data, client):
    """
    Test for bootcamp run detail view in happy path
    """
    user, _, bootcamp_run = test_data
    bootcamp_run_detail_url = reverse('bootcamp-run-detail', kwargs={'username': user.username, 'run_key': bootcamp_run.run_key})
    client.force_login(user)

    response = client.get(bootcamp_run_detail_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert sorted(list(response_json.keys())) == sorted(BOOTCAMP_RUN_FIELDS)
    assert response_json['run_key'] == bootcamp_run.run_key


def test_bootcamp_run_detail_fake_run(test_data, client):
    """
    Test if a request is made for a not existing bootcamp run
    """
    user, _, _ = test_data
    bootcamp_run_detail_url = reverse('bootcamp-run-detail', kwargs={'username': user.username, 'run_key': 123456789})
    client.force_login(user)
    assert client.get(bootcamp_run_detail_url).status_code == status.HTTP_404_NOT_FOUND


def test_bootcamp_run_list(test_data, client):
    """
    Test for bootcamp run list view in happy path
    """
    user, _, _ = test_data
    bootcamp_run_list_url = reverse('bootcamp-run-list', kwargs={'username': user.username})
    client.force_login(user)

    response = client.get(bootcamp_run_list_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 3
    for resp in response_json:
        assert sorted(list(resp.keys())) == sorted(BOOTCAMP_RUN_FIELDS)


def test_bootcamp_run_list_with_no_authorized_runs(test_data, client, mocker):
    """
    The view returns an empty list if no authorized bootcamp runs for the user are found
    """
    user, _, _ = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_bootcamp_run_keys',
        new_callable=PropertyMock,
        return_value=[],
    )
    bootcamp_run_list_url = reverse('bootcamp-run-list', kwargs={'username': user.username})
    client.force_login(user)

    response = client.get(bootcamp_run_list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_bootcamp_run_list_paid_with_no_authorized_runs(test_data, fulfilled_order, client, mocker):
    """
    The view returns the paid bootcamp runs even if if no authorized bootcamp runs for the user are found
    """
    user, _, bootcamp_run = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_bootcamp_run_keys',
        new_callable=PropertyMock,
        return_value=[],
    )

    bootcamp_run_list_url = reverse('bootcamp-run-list', kwargs={'username': user.username})
    client.force_login(user)
    response = client.get(bootcamp_run_list_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]['run_key'] == bootcamp_run.run_key
    assert response_json[0]['is_user_eligible_to_pay'] is False


def test_user_bootcamp_run_statement(test_data, fulfilled_order, client):
    """
    Test that the user bootcamp run statement view returns the expected filled-in template
    """
    user, _, bootcamp_run = test_data
    bootcamp_run_statement_url = reverse('bootcamp-run-statement', kwargs={'run_key': bootcamp_run.run_key})
    client.force_login(user)

    response = client.get(bootcamp_run_statement_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.template_name == 'bootcamp/statement.html'
    rendered_template_content = response.content.decode('utf-8')
    # User's full name should be in the statement
    assert response.data['user']['full_name'] in rendered_template_content
    # Bootcamp run title should be in the statement
    assert response.data['bootcamp_run']['display_title'] in rendered_template_content
    # Total payment amount should be in the statement
    assert '${}'.format(response.data['bootcamp_run']['total_paid']) in rendered_template_content
    # Each individual payment should be in the statement
    line_payments = fulfilled_order.line_set.values_list('price', flat=True)
    for line_payment in line_payments:
        assert '${}'.format(line_payment) in rendered_template_content


def test_user_bootcamp_run_statement_without_order(test_data, client):
    user, _, bootcamp_run = test_data
    bootcamp_run_statement_url = reverse('bootcamp-run-statement', kwargs={'run_key': bootcamp_run.run_key})
    client.force_login(user)

    response = client.get(bootcamp_run_statement_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
