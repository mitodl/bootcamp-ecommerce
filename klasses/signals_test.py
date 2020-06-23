""" Tests for applications.signals"""
import pytest

from klasses.factories import BootcampFactory

pytestmark = pytest.mark.django_db

# pylint: disable=redefined-outer-name


def test_bootcamp_signal(mocker):
    """Test that hubspot is synced whenever a Bootcamp is created/updated"""
    mock_hubspot = mocker.patch("klasses.signals.sync_hubspot_product")
    bootcamp = BootcampFactory.create()
    bootcamp.save()
    bootcamp.save()
    assert mock_hubspot.call_count == 3  # Once for creation, twice for updates
    mock_hubspot.assert_any_call(bootcamp)
