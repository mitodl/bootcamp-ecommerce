"""Sentry setup and configuration"""
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry(*, dsn, environment, version, log_level):
    """
    Initializes sentry
    Args:
        dsn (str): the sentry DSN key
        environment (str): the application environment
        version (str): the version of the application
        log_level (str): the sentry log level
    """
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=version,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            LoggingIntegration(level=log_level),
        ],
    )
