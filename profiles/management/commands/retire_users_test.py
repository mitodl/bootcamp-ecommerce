"""retire user test"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from social_django.models import UserSocialAuth
from mitol.common.utils import now_in_utc

from applications.factories import BootcampApplicationFactory

from jobma.factories import InterviewFactory, JobFactory
from profiles.factories import UserFactory, UserSocialAuthFactory
from profiles.management.commands import retire_users

from klasses.factories import BootcampRunFactory

User = get_user_model()

COMMAND = retire_users.Command()


@pytest.mark.django_db
def test_single_success():
    """test retire_users command success with one user"""
    test_username = "test_user"

    user = UserFactory.create(username=test_username, is_active=True)
    UserSocialAuthFactory.create(user=user, provider="edX")

    assert user.is_active is True
    assert "retired_email" not in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 1

    COMMAND.handle("retire_users", users=[test_username])

    user.refresh_from_db()
    assert user.is_active is False
    assert "retired_email" in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_multiple_success():
    """test retire_users command success with more than one user"""
    test_usernames = ["foo", "bar", "baz"]

    for username in test_usernames:
        user = UserFactory.create(username=username, is_active=True)
        UserSocialAuthFactory.create(user=user, provider="not_edx")

        assert user.is_active is True
        assert "retired_email" not in user.email
        assert UserSocialAuth.objects.filter(user=user).count() == 1

    COMMAND.handle("retire_users", users=test_usernames)

    for user_name in test_usernames:
        user = User.objects.get(username=user_name)
        assert user.is_active is False
        assert "retired_email" in user.email
        assert UserSocialAuth.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_retire_user_with_email():
    """test retire_users command success with user email"""
    test_email = "test@email.com"

    user = UserFactory.create(email=test_email, is_active=True)
    UserSocialAuthFactory.create(user=user, provider="edX")

    assert user.is_active is True
    assert "retired_email" not in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 1

    COMMAND.handle("retire_users", users=[test_email])

    user.refresh_from_db()
    assert user.is_active is False
    assert "retired_email" in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 0


@pytest.mark.django_db
def test_interview_applications_expired():
    """test retire_users command change the status of interviews to expired"""
    test_username = "test_user"

    user = UserFactory.create(username=test_username, is_active=True)
    UserSocialAuthFactory.create(user=user, provider="edX")

    assert user.is_active is True
    assert "retired_email" not in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 1

    now = now_in_utc()
    run = BootcampRunFactory.create(start_date=(now + timedelta(days=10)))

    bootcamp_app = BootcampApplicationFactory.create(
        state="AWAITING_USER_SUBMISSIONS", bootcamp_run=run
    )
    interview = InterviewFactory.create(
        job=JobFactory.create(run=bootcamp_app.bootcamp_run), applicant=user
    )

    COMMAND.handle("retire_users", users=[test_username])

    user.refresh_from_db()
    interview.refresh_from_db()
    assert user.is_active is False
    assert "retired_email" in user.email
    assert UserSocialAuth.objects.filter(user=user).count() == 0
    assert interview.status == "expired"
