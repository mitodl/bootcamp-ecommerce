"""
Validate that our settings functions work
"""

import sys
from types import SimpleNamespace

import pytest
from django.conf import settings
from django.core import mail
import semantic_version
from mitol.common import envs, pytest_utils


# pylint: disable=redefined-outer-name, unused-argument


# this is a test, but pylint thinks it ends up being unused
# hence we import the entire module and assign it here
test_app_json_modified = pytest_utils.test_app_json_modified


@pytest.fixture(autouse=True)
def settings_sandbox(monkeypatch):
    """Cleanup settings after a test"""

    monkeypatch.delenv("BOOTCAMP_DB_DISABLE_SSL", raising=False)
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "main.settings")
    monkeypatch.setenv("MAILGUN_SENDER_DOMAIN", "mailgun.fake.domain")
    monkeypatch.setenv("MAILGUN_KEY", "fake_mailgun_key")
    monkeypatch.setenv("BOOTCAMP_ECOMMERCE_BASE_URL", "http://localhost:8053")

    def _get():
        return vars(sys.modules["main.settings"])

    def _patch(overrides):
        for key, value in overrides.items():
            monkeypatch.setenv(key, value)

        return _reload()

    def _reload():
        """
        Reload settings module with cleanup to restore it.

        Returns:
            dict: dictionary of the newly reloaded settings ``vars``
        """
        envs.env.reload()
        return _get()

    yield SimpleNamespace(
        patch=_patch,
        reload=_reload,
        get=_get,
    )

    _reload()


def test_admin_settings(settings, settings_sandbox):
    """Verify that we configure email with environment variable"""

    settings_vars = settings_sandbox.patch(
        {
            "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
            "BOOTCAMP_ADMIN_EMAIL": "",
        }
    )
    assert settings_vars["ADMINS"] == ()

    test_admin_email = "cuddle_bunnies@example.com"
    settings_vars = settings_sandbox.patch(
        {
            "BOOTCAMP_ECOMMERCE_BASE_URL": "http://bootcamp.example.com",
            "BOOTCAMP_ADMIN_EMAIL": test_admin_email,
        }
    )
    assert (("Admins", test_admin_email),) == settings_vars["ADMINS"]
    # Manually set ADMIN to our test setting and verify e-mail
    # goes where we expect
    settings.ADMINS = (("Admins", test_admin_email),)
    mail.mail_admins("Test", "message")
    assert test_admin_email in mail.outbox[0].to


def test_db_ssl_enable(monkeypatch, settings_sandbox):
    """Verify that we can enable/disable database SSL with a var"""
    # Check default state is SSL on
    settings_vars = settings_sandbox.reload()
    assert settings_vars["DATABASES"]["default"]["OPTIONS"] == {"sslmode": "require"}

    # Check enabling the setting explicitly
    settings_vars = settings_sandbox.patch({"BOOTCAMP_DB_DISABLE_SSL": "True"})
    assert settings_vars["DATABASES"]["default"]["OPTIONS"] == {}

    # Disable it
    settings_vars = settings_sandbox.patch({"BOOTCAMP_DB_DISABLE_SSL": "False"})
    assert settings_vars["DATABASES"]["default"]["OPTIONS"] == {"sslmode": "require"}


def test_semantic_version():
    """
    Verify that we have a semantic compatible version.
    """
    semantic_version.Version(settings.VERSION)
