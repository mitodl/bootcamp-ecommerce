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


REQUIRED = {
    'FLUIDREVIEW_WEBHOOK_AUTH_TOKEN': 'asdfasdf',
}


class TestSettings(TestCase):
    """Validate that settings work as expected."""

    def reload_settings(self):
        """
        Reload settings module with cleanup to restore it.

        Returns:
            dict: dictionary of the newly reloaded settings ``vars``
        """
        importlib.reload(sys.modules['bootcamp.settings'])
        # Restore settings to original settings after test
        self.addCleanup(importlib.reload, sys.modules['bootcamp.settings'])
        return vars(sys.modules['bootcamp.settings'])

    def test_admin_settings(self):
        """Verify that we configure email with environment variable"""

        with mock.patch.dict('os.environ', {
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_ADMIN_EMAIL': '',
            **REQUIRED,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertFalse(settings_vars.get('ADMINS', False))

        test_admin_email = 'cuddle_bunnies@example.com'
        with mock.patch.dict('os.environ', {
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_ADMIN_EMAIL': test_admin_email,
            **REQUIRED,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertEqual(
                (('Admins', test_admin_email),),
                settings_vars['ADMINS']
            )
        # Manually set ADMIN to our test setting and verify e-mail
        # goes where we expect
        settings.ADMINS = (('Admins', test_admin_email),)
        mail.mail_admins('Test', 'message')
        self.assertIn(test_admin_email, mail.outbox[0].to)

    def test_db_ssl_enable(self):
        """Verify that we can enable/disable database SSL with a var"""

        # Check default state is SSL on
        with mock.patch.dict('os.environ', {
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            **REQUIRED,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertEqual(
                settings_vars['DATABASES']['default']['OPTIONS'],
                {'sslmode': 'require'}
            )

        # Check enabling the setting explicitly
        with mock.patch.dict('os.environ', {
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_DB_DISABLE_SSL': 'True',
            **REQUIRED,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertEqual(
                settings_vars['DATABASES']['default']['OPTIONS'],
                {}
            )

        # Disable it
        with mock.patch.dict('os.environ', {
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_DB_DISABLE_SSL': 'False',
            **REQUIRED,
        }, clear=True):
            settings_vars = self.reload_settings()
            self.assertEqual(
                settings_vars['DATABASES']['default']['OPTIONS'],
                {'sslmode': 'require'}
            )

    @staticmethod
    def test_semantic_version():
        """
        Verify that we have a semantic compatible version.
        """
        semantic_version.Version(settings.VERSION)
