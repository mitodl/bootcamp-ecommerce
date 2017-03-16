"""
Test end to end django views.
"""
import json
from unittest.mock import patch

from django.test import TestCase
from django.core.urlresolvers import reverse
from factory.fuzzy import FuzzyText
from rest_framework.status import HTTP_302_FOUND

from bootcamp.factories import UserFactory


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """

    def test_index_view(self):
        """Verify the index view is as expected"""
        response = self.client.get(reverse('bootcamp-index'))
        self.assertContains(
            response,
            "Log in using your edx.org account",
            status_code=200
        )

    def test_webpack_url(self):
        """Verify that webpack bundle src shows up in production"""

        host = FuzzyText().fuzz()
        edx_base_url = FuzzyText().fuzz()
        environment = FuzzyText().fuzz()
        email_support = FuzzyText().fuzz()
        version = '0.0.1'
        with self.settings(
            WEBPACK_DEV_SERVER_HOST=host,
            VERSION=version,
            EDXORG_BASE_URL=edx_base_url,
            ENVIRONMENT=environment,
            EMAIL_SUPPORT=email_support,
        ), patch('bootcamp.templatetags.render_bundle._get_bundle') as get_bundle:
            response = self.client.get('/')

        bundles = [bundle[0][1] for bundle in get_bundle.call_args_list]
        assert set(bundles) == {
            'common',
            'root',
            'sentry_client',
            'style',
        }

        js_settings = json.loads(response.context['js_settings_json'])
        assert js_settings == {
            'environment': environment,
            'host': host,
            'release_version': version,
            'sentry_dsn': None,
            'public_path': '/static/bundles/',
            'support_email': email_support,
            'edx_base_url': edx_base_url,
        }

    def test_pay_anonymous(self):
        """
        Test that anonymous users can't see the anonymous view
        """
        assert self.client.get(reverse('pay')).status_code == HTTP_302_FOUND

    def test_pay(self):
        """
        Test that logged in users can see the payment page
        """
        user = UserFactory.create()
        self.client.force_login(user)
        resp = self.client.get(reverse('pay'))
        self.assertContains(resp, "{full}, Welcome to MIT Bootcamps".format(full=user.get_full_name()))
        self.assertContains(resp, "Make a payment of")
