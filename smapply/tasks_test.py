"""Tests for smappply tasks"""

import pytest

from profiles.models import Profile
from smapply.tasks import sync_all_users

pytestmark = pytest.mark.django_db

test_user_data = [
    {'id': 12345678, 'first_name': 'first_name', 'last_name': 'last_name',
     'email': 'test1@test.co', 'last_login': '2019-08-04T08:27:55', 'date_joined': '2012-10-21T17:37:03',
     'timezone': 'Europe/Berlin', 'groups': [], 'teams': [], 'member_of': [], 'submissions': [], 'status': 0,
     'status_pretty': 'Active', 'roles': 'Applicant', 'role_ids': [1], 'assignments_total': 0,
     'assignments_completed': 0, 'recommendations': [], 'recommendations_completed': [], 'awards_applied_to': [],
     'last_login_pretty': 'Aug 4 2019', 'date_joined_pretty': 'Oct 21 2012', 'team_names': '',
     'custom_fields': {'43316': ''}, 'signup_source': '-', 'verified': 'True', 'organizations': [], 'sso_id': [],
     'applicants_conflicted': 0, 'applications_with_awarded_money_count': 0},
    {'id': 87654321, 'first_name': 'testy', 'last_name': 'testname',
     'email': 'tester@test.co', 'last_login': '2019-08-04T08:27:55', 'date_joined': '2012-10-21T17:37:03',
     'timezone': 'Europe/Berlin', 'groups': [], 'teams': [], 'member_of': [], 'submissions': [], 'status': 0,
     'status_pretty': 'Active', 'roles': 'Applicant', 'role_ids': [1], 'assignments_total': 0,
     'assignments_completed': 0, 'recommendations': [], 'recommendations_completed': [], 'awards_applied_to': [],
     'last_login_pretty': 'Aug 4 2019', 'date_joined_pretty': 'Oct 21 2012', 'team_names': '',
     'custom_fields': {'43316': ''}, 'signup_source': '-', 'verified': 'True', 'organizations': [], 'sso_id': [],
     'applicants_conflicted': 0, 'applications_with_awarded_money_count': 0}
]


def test_sync_all_users(mocker):
    """
    Test that sync_all_users properly parses smapply data
    """
    mocker.patch(
        'smapply.tasks.list_users',
        return_value=test_user_data,
    )
    sync_all_users()
    assert Profile.objects.count() == 2

    sync_all_users()
    assert Profile.objects.count() == 2


def test_sync_all_users_bad_data(mocker):
    """
    Test that sync_all_users properly skips bad data
    """
    test_user_data[0].pop('email')
    mocker.patch(
        'smapply.tasks.list_users',
        return_value=test_user_data,
    )
    sync_all_users()
    assert Profile.objects.count() == 1
