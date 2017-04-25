"""
Test end to end django views.
"""
import json
from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from factory.fuzzy import FuzzyText
from rest_framework.status import HTTP_302_FOUND

from profiles.factories import ProfileFactory


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = ProfileFactory.create().user

    def test_index_anonymous(self):
        """Verify the index view is as expected when user is anonymous"""

        host = FuzzyText().fuzz()
        environment = FuzzyText().fuzz()
        version = '0.0.1'
        with self.settings(
            WEBPACK_DEV_SERVER_HOST=host,
            VERSION=version,
            ENVIRONMENT=environment,
        ), patch('bootcamp.templatetags.render_bundle._get_bundle') as get_bundle:
            resp = self.client.get('/')
        self.assertContains(
            resp,
            "Log in using your edx.org account",
            status_code=200
        )

        bundles = [bundle[0][1] for bundle in get_bundle.call_args_list]
        assert set(bundles) == {
            'common',
            'sentry_client',
            'style',
        }
        js_settings = json.loads(resp.context['js_settings_json'])
        assert js_settings == {
            'environment': environment,
            'release_version': version,
            'sentry_dsn': None,
            'public_path': '/static/bundles/',
        }

    def test_index_logged_in(self):
        """Verify the user is redirected to pay if logged in"""
        self.client.force_login(self.user)
        assert self.client.get(reverse('bootcamp-index')).status_code == HTTP_302_FOUND

    def test_pay_anonymous(self):
        """
        Test that anonymous users can't see the anonymous view
        """
        assert self.client.get(reverse('pay')).status_code == HTTP_302_FOUND

    def test_pay(self):
        """
        Test that logged in users can see the payment page
        """
        self.client.force_login(self.user)
        host = FuzzyText().fuzz()
        environment = FuzzyText().fuzz()
        version = '0.0.1'
        with self.settings(
            WEBPACK_DEV_SERVER_HOST=host,
            VERSION=version,
            ENVIRONMENT=environment,
        ), patch('bootcamp.templatetags.render_bundle._get_bundle') as get_bundle:
            resp = self.client.get(reverse('pay'))

        bundles = [bundle[0][1] for bundle in get_bundle.call_args_list]
        assert set(bundles) == {
            'common',
            'payment',
            'sentry_client',
            'style',
        }

        js_settings = json.loads(resp.context['js_settings_json'])
        assert js_settings == {
            'environment': environment,
            'full_name': self.user.profile.name,
            'release_version': version,
            'sentry_dsn': None,
            'public_path': '/static/bundles/',
        }
