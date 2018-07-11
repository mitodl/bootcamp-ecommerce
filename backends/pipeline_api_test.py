"""
pipeline Tests
"""
from unittest import mock
from urllib.parse import urljoin
import ddt

from django.test import TestCase

from backends import pipeline_api, edxorg
from backends.utils import get_social_username
from profiles.factories import UserFactory


@ddt.ddt
class PipelineTests(TestCase):
    """pipeline tests"""

    def setUp(self):
        """
        Set up class
        """
        super(PipelineTests, self).setUp()
        self.user = UserFactory.create()
        self.user.social_auth.create(
            provider='not_edx',
        )
        self.user.social_auth.create(
            provider=edxorg.EdxOrgOAuth2.name,
            uid="{}_edx".format(self.user.username),
        )

    @ddt.data(True, False)
    @mock.patch('backends.edxorg.EdxOrgOAuth2.get_json')
    def test_update_email(self, is_new, mocked_get_json):
        """
        Test email changed for new user.
        """
        mocked_content = {
            'email': 'foo@example.com'
        }
        mocked_get_json.return_value = mocked_content
        pipeline_api.update_profile_from_edx(
            edxorg.EdxOrgOAuth2(strategy=mock.Mock()), self.user, {'access_token': 'foo_token'}, is_new)
        mocked_get_json.assert_called_once_with(
            urljoin(
                edxorg.EdxOrgOAuth2.EDXORG_BASE_URL,
                '/api/user/v1/accounts/{0}'.format(get_social_username(self.user))
            ),
            headers={'Authorization': 'Bearer foo_token'}
        )

        assert self.user.email == mocked_content['email']
