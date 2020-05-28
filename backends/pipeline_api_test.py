"""
pipeline Tests
"""
from urllib.parse import urljoin

import pytest

from backends import pipeline_api, edxorg
from backends.utils import get_social_username


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("is_new", [True, False])
def test_update_email(mocker, user, is_new):
    """
    Test email changed for new user.
    """
    mocked_get_json = mocker.patch("backends.edxorg.EdxOrgOAuth2.get_json")

    mocked_content = {"email": "foo@example.com"}
    mocked_get_json.return_value = mocked_content
    pipeline_api.update_profile_from_edx(
        edxorg.EdxOrgOAuth2(strategy=mocker.Mock()),
        user,
        {"access_token": "foo_token"},
        is_new,
    )
    mocked_get_json.assert_called_once_with(
        urljoin(
            edxorg.EdxOrgOAuth2.EDXORG_BASE_URL,
            "/api/user/v1/accounts/{0}".format(get_social_username(user)),
        ),
        headers={"Authorization": "Bearer foo_token"},
    )

    assert user.email == mocked_content["email"]
