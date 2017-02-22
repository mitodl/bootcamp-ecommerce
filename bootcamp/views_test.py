"""
Test end to end django views.
"""
import json
from unittest.mock import patch

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from factory.fuzzy import FuzzyText


class TestViews(TestCase):
    """
    Test that the views work as expected.
    """
    def setUp(self):
        """Common test setup"""
        super(TestViews, self).setUp()
        self.client = Client()

    def test_index_view(self):
        """Verify the index view is as expected"""
        response = self.client.get(reverse('bootcamp-index'))
        self.assertContains(
            response,
            "Hi, I'm bootcamp-ecommerce",
            status_code=200
        )

    def test_webpack_url(self):
        """Verify that webpack bundle src shows up in production"""

        ga_tracking_id = FuzzyText().fuzz()
        host = FuzzyText().fuzz()
        edx_base_url = FuzzyText().fuzz()
        environment = FuzzyText().fuzz()
        email_support = FuzzyText().fuzz()
        react_ga_debug = FuzzyText().fuzz()
        version = '0.0.1'
        with self.settings(
            GA_TRACKING_ID=ga_tracking_id,
            WEBPACK_DEV_SERVER_HOST=host,
            VERSION=version,
            EDXORG_BASE_URL=edx_base_url,
            ENVIRONMENT=environment,
            EMAIL_SUPPORT=email_support,
            REACT_GA_DEBUG=react_ga_debug,
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
                'gaTrackingID': ga_tracking_id,
                'host': host,
                'release_version': version,
                'sentry_dsn': None,
                'public_path': '/static/bundles/',
                'support_email': email_support,
                'edx_base_url': edx_base_url,
                'reactGaDebug': react_ga_debug,
            }
