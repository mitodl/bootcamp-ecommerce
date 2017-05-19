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
from klasses.factories import KlassFactory
from profiles.factories import ProfileFactory


# pylint: disable=missing-docstring,redefined-outer-name,unused-argument

pytestmark = pytest.mark.django_db


KLASS_FIELDS = [
    'klass_key',
    'start_date',
    'end_date',
    'total_paid',
    'installments',
    'payments',
    'klass_name',
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
        klass = KlassFactory.create()

    patch_get_admissions(mocker, user)
    # just need one klass, so returning the last created
    return user, other_user, klass


@pytest.fixture()
def fulfilled_order(test_data):
    user, _, klass = test_data
    order = OrderFactory.create(user=user, status=Order.FULFILLED)
    LineFactory.create(order=order, klass_key=klass.klass_key, price=123.45)
    return order


def test_only_self_can_access_apis(test_data, client):
    """
    Only the the requester user can access her own info
    """
    user, other_user, klass = test_data
    detail_url_user = reverse('klass-detail', kwargs={'username': user.username, 'klass_key': klass.klass_key})
    detail_url_other_user = reverse(
        'klass-detail', kwargs={'username': other_user.username, 'klass_key': klass.klass_key})
    list_url_user = reverse('klass-list', kwargs={'username': user.username})
    list_url_other_user = reverse('klass-list', kwargs={'username': other_user.username})

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


def test_klass_detail(test_data, client):
    """
    Test for klass detail view in happy path
    """
    user, _, klass = test_data
    klass_detail_url = reverse('klass-detail', kwargs={'username': user.username, 'klass_key': klass.klass_key})
    client.force_login(user)

    response = client.get(klass_detail_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert sorted(list(response_json.keys())) == sorted(KLASS_FIELDS)
    assert response_json['klass_key'] == klass.klass_key


def test_klass_detail_fake_klass(test_data, client):
    """
    Test if a request is made for a not existing klass
    """
    user, _, _ = test_data
    klass_detail_url = reverse('klass-detail', kwargs={'username': user.username, 'klass_key': 123456789})
    client.force_login(user)
    assert client.get(klass_detail_url).status_code == status.HTTP_404_NOT_FOUND


def test_klass_list(test_data, client):
    """
    Test for klass list view in happy path
    """
    user, _, _ = test_data
    klass_list_url = reverse('klass-list', kwargs={'username': user.username})
    client.force_login(user)

    response = client.get(klass_list_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 3
    for klass_resp in response_json:
        assert sorted(list(klass_resp.keys())) == sorted(KLASS_FIELDS)


def test_klass_list_with_no_authorized_klasses(test_data, client, mocker):
    """
    The view returns an empty list if no authorized klasses for the user are found
    """
    user, _, _ = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_klasses_keys',
        new_callable=PropertyMock,
        return_value=[],
    )
    klass_list_url = reverse('klass-list', kwargs={'username': user.username})
    client.force_login(user)

    response = client.get(klass_list_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_klass_list_paid_klass_with_no_authorized_klasses(test_data, fulfilled_order, client, mocker):
    """
    The view returns the paid klasses even if if no authorized klasses for the user are found
    """
    user, _, klass = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_klasses_keys',
        new_callable=PropertyMock,
        return_value=[],
    )

    klass_list_url = reverse('klass-list', kwargs={'username': user.username})
    client.force_login(user)
    response = client.get(klass_list_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]['klass_key'] == klass.klass_key
    assert response_json[0]['is_user_eligible_to_pay'] is False


def test_user_klass_statement(test_data, fulfilled_order, client):
    """
    Test that the user klass statement view returns the expected filled-in template
    """
    user, _, klass = test_data
    klass_statement_url = reverse('klass-statement', kwargs={'klass_key': klass.klass_key})
    client.force_login(user)

    response = client.get(klass_statement_url)
    assert response.status_code == status.HTTP_200_OK
    assert response.template_name == 'bootcamp/statement.html'
    rendered_template_content = response.content.decode('utf-8')
    # User's full name should be in the statement
    assert response.data['user']['full_name'] in rendered_template_content
    # Bootcamp klass title should be in the statement
    assert response.data['klass']['display_title'] in rendered_template_content
    # Total payment amount should be in the statement
    assert '${}'.format(response.data['klass']['total_paid']) in rendered_template_content
    # Each individual payment should be in the statement
    line_payments = fulfilled_order.line_set.values_list('price', flat=True)
    for line_payment in line_payments:
        assert '${}'.format(line_payment) in rendered_template_content


def test_user_klass_statement_without_order(test_data, client):
    user, _, klass = test_data
    klass_statement_url = reverse('klass-statement', kwargs={'klass_key': klass.klass_key})
    client.force_login(user)

    response = client.get(klass_statement_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND
