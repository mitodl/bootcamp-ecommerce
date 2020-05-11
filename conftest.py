"""Global fixtures"""
# pylint: disable=wildcard-import,unused-wildcard-import
from django.conf import settings
from fixtures.common import *
from fixtures.autouse import *
from fixtures.cybersource import *

TEST_MEDIA_ROOT = "/var/media/test_media_root"


def pytest_configure():
    """Pytest hook to perform some initial configuration"""
    # HACK: Overwriting MEDIA_ROOT setting to ensure that files end up in a temp directory. pytest-django's 'settings'
    # fixture can't be used here, and an environment variable can't be used because we don't yet have a way to define
    # env vars that will be set exclusively for the test suite when Docker containers are spun up.
    settings.MEDIA_ROOT = TEST_MEDIA_ROOT
