"""
Validate that our settings functions work
"""

import importlib
import json
import sys
from unittest import mock

from django.conf import settings
from django.core import mail
from django.test import TestCase
import semantic_version

from main import envs

REQUIRED = {
    'FLUIDREVIEW_WEBHOOK_AUTH_TOKEN': 'asdfasdf',
}


def cleanup_settings():
    """Cleanup settings after a test"""
    envs.env.reload()
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
        importlib.reload(sys.modules['main.settings'])
        # Restore settings to original settings after test
        self.addCleanup(cleanup_settings)
        return vars(sys.modules['main.settings'])

    def test_admin_settings(self):
        """Verify that we configure email with environment variable"""

        settings_vars = self.patch_settings({
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_ADMIN_EMAIL': '',
            **REQUIRED,
        })
        self.assertFalse(settings_vars.get('ADMINS', False))

        test_admin_email = 'cuddle_bunnies@example.com'
        settings_vars = self.patch_settings({
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_ADMIN_EMAIL': test_admin_email,
            **REQUIRED,
        })
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
        settings_vars = self.patch_settings({
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            **REQUIRED,
        })
        self.assertEqual(
            settings_vars['DATABASES']['default']['OPTIONS'],
            {'sslmode': 'require'}
        )

        # Check enabling the setting explicitly
        settings_vars = self.patch_settings({
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_DB_DISABLE_SSL': 'True',
            **REQUIRED,
        })
        self.assertEqual(
            settings_vars['DATABASES']['default']['OPTIONS'],
            {}
        )

        # Disable it
        settings_vars = self.patch_settings({
            'BOOTCAMP_ECOMMERCE_BASE_URL': 'http://bootcamp.example.com',
            'BOOTCAMP_DB_DISABLE_SSL': 'False',
            **REQUIRED,
        })
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

    @staticmethod
    def test_app_json_modified():
        """
        generate_app_json should return a dictionary of JSON config for app.json
        """
        from main.envs import generate_app_json

        with open("app.json") as app_json_file:
            app_json = json.load(app_json_file)

        generated_app_json = generate_app_json()

        # pytest will print the difference
        assert json.dumps(app_json, sort_keys=True, indent=2) == json.dumps(
            generated_app_json, sort_keys=True, indent=2
        ), "Generated app.json does not match the app.json file. Please use the 'generate_app_json' management command to update app.json"
