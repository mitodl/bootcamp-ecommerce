""" Tests for applications.signals"""
import pytest

from klasses.factories import BootcampRunFactory

pytestmark = pytest.mark.django_db

# pylint: disable=redefined-outer-name


def test_bootcamp_run_signal(mocker):
    """Test that hubspot is synced whenever a Bootcamp is created/updated"""
    mock_on_commit = mocker.patch("klasses.signals.on_commit")
    bootcamp = BootcampRunFactory.create()
    bootcamp.save()
    bootcamp.save()
    assert mock_on_commit.call_count == 3  # Once for creation, twice for updates
