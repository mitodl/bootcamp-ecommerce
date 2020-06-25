""" Tests for applications.signals"""
import pytest

from klasses.factories import BootcampRunFactory

pytestmark = pytest.mark.django_db

# pylint: disable=redefined-outer-name


def test_bootcamp_run_signal(mocker):
    """Test that hubspot is synced whenever a Bootcamp is created/updated"""
    mock_hubspot = mocker.patch("klasses.signals.sync_hubspot_product")
    bootcamp_run = BootcampRunFactory.create()
    bootcamp_run.save()
    bootcamp_run.save()
    assert mock_hubspot.call_count == 3  # Once for creation, twice for updates
    mock_hubspot.assert_any_call(bootcamp_run)
