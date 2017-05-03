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
from profiles.factories import UserFactory


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
    'is_user_eligible_to_pay',
    'payment_deadline',
    'price',
]


@pytest.fixture()
def test_data(mocker):
    """
    Sets up the data for all the tests in this module
    """
    user = UserFactory.create()
    user.social_auth.create(
        provider=EdxOrgOAuth2.name,
        uid=user.username,
        extra_data={"access_token": "fooooootoken"}
    )
    other_user = UserFactory.create()

    for _ in range(3):
        klass = KlassFactory.create()

    patch_get_admissions(mocker, user)
    # just need one klass, so returning the last created
    return user, other_user, klass


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


def test_klass_list_paid_klass_with_no_authorized_klasses(test_data, client, mocker):
    """
    The view returns the paid klasses even if if no authorized klasses for the user are found
    """
    user, _, klass = test_data
    mocker.patch(
        'klasses.bootcamp_admissions_client.BootcampAdmissionClient.payable_klasses_keys',
        new_callable=PropertyMock,
        return_value=[],
    )
    order = OrderFactory.create(user=user, status=Order.FULFILLED)
    LineFactory.create(order=order, klass_key=klass.klass_key, price=123.45)

    klass_list_url = reverse('klass-list', kwargs={'username': user.username})
    client.force_login(user)
    response = client.get(klass_list_url)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    assert response_json[0]['klass_key'] == klass.klass_key
    assert response_json[0]['is_user_eligible_to_pay'] is False
