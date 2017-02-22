"""
Test end to end django views.
"""
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


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
        for debug, expected_url in [
                (True, "foo_server/style.js"),
                (False, "bundles/style.js")
        ]:
            with self.settings(
                DEBUG=debug,
                USE_WEBPACK_DEV_SERVER=True,
                WEBPACK_SERVER_URL="foo_server"
            ):
                response = self.client.get(reverse('bootcamp-index'))
                self.assertContains(
                    response,
                    expected_url,
                    status_code=200
                )
