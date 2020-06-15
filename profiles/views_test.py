"""Test for user views"""
from datetime import timedelta
import pytest

from django.urls import reverse
from rest_framework import status
from social_django.models import UserSocialAuth

from main.test_utils import any_instance_of
from main.utils import now_in_utc
from profiles.factories import UserFactory
from profiles.models import ChangeEmailRequest


@pytest.mark.django_db
def test_cannot_create_user(client):
    """Verify the api to create a user is nonexistent"""
    resp = client.post("/api/users/", data={"name": "Name"})

    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_update_user(user_client, user):
    """Verify the api to update a user is doesn't accept the verb"""
    resp = user_client.patch(
        reverse("users_api-detail", kwargs={"pk": user.id}), data={"name": "Name"}
    )

    assert resp.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_get_user_by_id(user_client, user):
    """Test that user can request their own user by id"""
    resp = user_client.get(reverse("users_api-detail", kwargs={"pk": user.id}))

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "legal_address": {
            "first_name": user.legal_address.first_name,
            "last_name": user.legal_address.last_name,
            "street_address": [user.legal_address.street_address_1],
            "city": user.legal_address.city,
            "state_or_territory": user.legal_address.state_or_territory,
            "country": user.legal_address.country,
            "postal_code": user.legal_address.postal_code,
        },
        "profile": {
            "name": user.profile.name,
            "gender": user.profile.gender,
            "company": user.profile.company,
            "company_size": user.profile.company_size,
            "job_title": user.profile.job_title,
            "birth_year": int(user.profile.birth_year),
            "job_function": user.profile.job_function,
            "years_experience": user.profile.years_experience,
            "highest_education": user.profile.highest_education,
            "industry": user.profile.industry,
            "is_complete": True,
            "updated_on": any_instance_of(str),
        },
        "is_anonymous": False,
        "is_authenticated": True,
    }


def test_get_user_by_me(user_client, user):
    """Test that user can request their own user by the 'me' alias"""
    resp = user_client.get(reverse("users_api-me"))

    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "legal_address": {
            "first_name": user.legal_address.first_name,
            "last_name": user.legal_address.last_name,
            "street_address": [user.legal_address.street_address_1],
            "city": user.legal_address.city,
            "state_or_territory": user.legal_address.state_or_territory,
            "country": user.legal_address.country,
            "postal_code": user.legal_address.postal_code,
        },
        "profile": {
            "name": user.profile.name,
            "gender": user.profile.gender,
            "company": user.profile.company,
            "company_size": user.profile.company_size,
            "job_title": user.profile.job_title,
            "birth_year": int(user.profile.birth_year),
            "job_function": user.profile.job_function,
            "years_experience": user.profile.years_experience,
            "highest_education": user.profile.highest_education,
            "industry": user.profile.industry,
            "is_complete": True,
            "updated_on": any_instance_of(str),
        },
        "is_anonymous": False,
        "is_authenticated": True,
    }


@pytest.mark.django_db
def test_countries_states_view(client):
    """Test that a list of countries and states is returned"""
    resp = client.get(reverse("countries_api-list"))
    countries = {country["code"]: country for country in resp.json()}
    assert len(countries.get("US").get("states")) > 50
    assert {"code": "CA-QC", "name": "Quebec"} in countries.get("CA").get("states")
    assert len(countries.get("FR").get("states")) == 0
    assert countries.get("US").get("name") == "United States"
    assert countries.get("TW").get("name") == "Taiwan"


def test_create_email_change_request_invalid_password(user_drf_client, user):
    """Test that invalid password is returned"""
    resp = user_drf_client.post(
        "/api/change-emails/",
        data={
            "new_email": "abc@example.com",
            "password": user.password,
            "old_password": "abc",
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_email_change_request_existing_email(user_drf_client, user):
    """Test that create change email request gives validation error for existing user email"""
    new_user = UserFactory.create()
    user_password = user.password
    user.set_password(user.password)
    user.save()
    resp = user_drf_client.post(
        "/api/change-emails/",
        data={"new_email": new_user.email, "password": user_password},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_email_change_request_same_email(user_drf_client, user):
    """Test that user same email wouldn't be processed"""
    resp = user_drf_client.post(
        "/api/change-emails/",
        data={
            "new_email": user.email,
            "password": user.password,
            "old_password": user.password,
        },
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST


def test_create_email_change_request_valid_email(user_drf_client, user, mocker):
    """Test that change request is created"""
    user_password = "PaSsWoRd"
    user.set_password(user_password)
    user.save()

    mock_email = mocker.patch("mail.v2.verification_api.send_verify_email_change_email")
    resp = user_drf_client.post(
        "/api/change-emails/",
        data={"new_email": "abc@example.com", "password": user_password},
    )

    assert resp.status_code == status.HTTP_201_CREATED

    code = mock_email.call_args[0][1].code
    assert code

    old_email = user.email
    resp = user_drf_client.patch(
        "/api/change-emails/{}/".format(code), data={"confirmed": True}
    )
    assert not UserSocialAuth.objects.filter(uid=old_email, user=user).exists()
    assert resp.status_code == status.HTTP_200_OK
    user.refresh_from_db()
    assert user.email == "abc@example.com"


def test_create_email_change_request_expired_code(user_drf_client, user):
    """Check for expired code for Email Change Request"""
    change_request = ChangeEmailRequest.objects.create(
        user=user,
        new_email="abc@example.com",
        expires_on=now_in_utc() - timedelta(seconds=5),
    )

    resp = user_drf_client.patch(
        "/api/change-emails/{}/".format(change_request.code), data={"confirmed": True}
    )
    assert resp.status_code == status.HTTP_404_NOT_FOUND


def test_update_email_change_request_invalid_token(user_drf_client):
    """Test that invalid token doesn't work"""
    resp = user_drf_client.patch("/api/change-emails/abc/", data={"confirmed": True})
    assert resp.status_code == status.HTTP_404_NOT_FOUND
