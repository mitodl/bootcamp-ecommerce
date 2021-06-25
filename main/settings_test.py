"""
Validate that our settings functions work
"""

import importlib
import sys
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase
import semantic_version
from mitol.common import envs, pytest_utils


# this is a test, but pylint thinks it ends up being unused
# hence we import the entire module and assign it here
test_app_json_modified = pytest_utils.test_app_json_modified


def cleanup_settings():
    """Cleanup settings after a test"""
    envs.env.reload()
    importlib.reload(sys.modules["mitol.common.settings.webpack"])
    importlib.reload(sys.modules["main.settings"])


class TestSettings(TestCase):
    """Validate that settings work as expected."""

    def patch_settings(self, values):
        """Patch the cached settings loaded by EnvParser"""
        with mock.patch.dict("os.environ", values, clear=True):
            envs.env.reload()
            settings_dict = self.reload_settings()
        return settings_dict

    def reload_settings(self):
        """
        Reload settings module with cleanup to restore it.

        Returns:
            dict: dictionary of the newly reloaded settings ``vars``
        """
        importlib.reload(sys.modules["main.settings"])
        # Restore settings to original settings after test
        self.addCleanup(cleanup_settings)
        return vars(sys.modules["main.settings"])

    def test_admin_settings(self):
        """Verify that we configure email with environment variable"""

        settings_vars = self.patch_settings(
            {
                "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
                "BOOTCAMP_ADMIN_EMAIL": "",
            }
        )
        self.assertFalse(settings_vars.get("ADMINS", False))

        test_admin_email = "cuddle_bunnies@example.com"
        settings_vars = self.patch_settings(
            {
                "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
                "BOOTCAMP_ADMIN_EMAIL": test_admin_email,
            }
        )
        self.assertEqual((("Admins", test_admin_email),), settings_vars["ADMINS"])
        # Manually set ADMIN to our test setting and verify e-mail
        # goes where we expect
        settings.ADMINS = (("Admins", test_admin_email),)
        mail.mail_admins("Test", "message")
        self.assertIn(test_admin_email, mail.outbox[0].to)

    def test_db_ssl_enable(self):
        """Verify that we can enable/disable database SSL with a var"""

        # Check default state is SSL on
        settings_vars = self.patch_settings(
            {"BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com"}
        )
        self.assertEqual(
            settings_vars["DATABASES"]["default"]["OPTIONS"], {"sslmode": "require"}
        )

        # Check enabling the setting explicitly
        settings_vars = self.patch_settings(
            {
                "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
                "BOOTCAMP_DB_DISABLE_SSL": "True",
            }
        )
        self.assertEqual(settings_vars["DATABASES"]["default"]["OPTIONS"], {})

        # Disable it
        settings_vars = self.patch_settings(
            {
                "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
                "BOOTCAMP_DB_DISABLE_SSL": "False",
            }
        )
        self.assertEqual(
            settings_vars["DATABASES"]["default"]["OPTIONS"], {"sslmode": "require"}
        )

    @staticmethod
    def test_semantic_version():
        """
        Verify that we have a semantic compatible version.
        """
        semantic_version.Version(settings.VERSION)
