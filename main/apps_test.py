"""Test for main app"""
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured

from main.apps import MainAppConfig


def test_bootcamp_mandatory_settings(settings):
    """Test that an exception is raised for missing mandatory settings"""
    for setting in settings.MANDATORY_SETTINGS:
        setattr(settings, setting, None)
    main = MainAppConfig('main', sys.modules[__name__])
    with pytest.raises(ImproperlyConfigured) as exception:
        main.ready()
    for setting in settings.MANDATORY_SETTINGS:
        assert setting in str(exception)
