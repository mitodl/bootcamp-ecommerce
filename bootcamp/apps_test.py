"""Test for bootcamp apps"""
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured

from bootcamp.apps import BootcampConfig


def test_bootcamp_mandatory_settings(settings):
    """Test that an exception is raised for missing mandatory settings"""
    for setting in settings.MANDATORY_SETTINGS:
        setattr(settings, setting, None)
    bootcamp = BootcampConfig('bootcamp', sys.modules[__name__])
    with pytest.raises(ImproperlyConfigured) as exception:
        bootcamp.ready()
    for setting in settings.MANDATORY_SETTINGS:
        assert setting in str(exception)
