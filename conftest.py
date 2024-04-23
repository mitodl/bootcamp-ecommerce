"""Global fixtures"""

# pylint: disable=wildcard-import,unused-wildcard-import
from django.conf import settings
from fixtures.common import *  # noqa: F403
from fixtures.autouse import *  # noqa: F403
from fixtures.cybersource import *  # noqa: F403

TEST_MEDIA_ROOT = "/var/media/test_media_root"


def pytest_addoption(parser):
    """Pytest hook that adds command line parameters"""
    parser.addoption(
        "--simple",
        action="store_true",
        help="Run tests only (no cov, no pylint, warning output silenced)",
    )


def pytest_cmdline_main(config):
    """Pytest hook that runs after command line options are parsed"""
    if getattr(config.option, "simple") is True:
        # Switch off pylint plugin
        config.option.pylint = False
        config.option.no_pylint = True


def pytest_configure(config):
    """Pytest hook to perform some initial configuration"""
    # HACK: Overwriting MEDIA_ROOT setting to ensure that files end up in a temp directory. pytest-django's 'settings'
    # fixture can't be used here, and an environment variable can't be used because we don't yet have a way to define
    # env vars that will be set exclusively for the test suite when Docker containers are spun up.
    settings.MEDIA_ROOT = TEST_MEDIA_ROOT
    if getattr(config.option, "simple") is True:
        # NOTE: These plugins are already configured by the time the pytest_cmdline_main hook is run, so we can't
        #       simply add/alter the command line options in that hook. This hook is being used to
        #       reconfigure/unregister plugins that we can't change via the pytest_cmdline_main hook.
        # Switch off coverage plugin
        cov = config.pluginmanager.get_plugin("_cov")
        cov.options.no_cov = True
        # Remove warnings plugin to suppress warnings
        if config.pluginmanager.has_plugin("warnings"):
            warnings_plugin = config.pluginmanager.get_plugin("warnings")
            config.pluginmanager.unregister(warnings_plugin)
