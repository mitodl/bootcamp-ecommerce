"""Tests for applications.signals"""

import pytest

from klasses.factories import BootcampRunFactory, PersonalPriceFactory
from klasses.signals import personal_price_post_delete, personal_price_post_save

pytestmark = pytest.mark.django_db


def test_bootcamp_run_signal(mocker):
    """Test that hubspot_sync is synced whenever a Bootcamp is created/updated"""
    mock_on_commit = mocker.patch("klasses.signals.on_commit")
    bootcamp = BootcampRunFactory.create()
    bootcamp.save()
    bootcamp.save()
    assert mock_on_commit.call_count == 3  # Once for creation, twice for updates


def test_personal_price_save_signal(mocker):
    """An API method to update a bootcamp application should be called after a personal price is created/saved"""
    mock_on_commit = mocker.patch("klasses.signals.on_commit")
    personal_price = PersonalPriceFactory.create()
    # This signal is called twice when the record is created (as opposed to just being saved)
    assert mock_on_commit.call_count == 2
    personal_price.save()
    assert mock_on_commit.call_count == 3
    # Test the function call from the signal handler
    patched_adjust_app = mocker.patch("klasses.signals.adjust_app_state_for_new_price")
    personal_price_post_save(mocker.Mock(), personal_price, False)  # noqa: FBT003
    # Call the function that was passed into "on_commit", which in this case should be our patched API function
    mock_on_commit.call_args[0][0]()
    patched_adjust_app.assert_called_once_with(
        user=personal_price.user,
        bootcamp_run=personal_price.bootcamp_run,
        new_price=personal_price.price,
    )


def test_personal_price_delete_signal(mocker):
    """An API method to update a bootcamp application should be called after a personal price is deleted"""
    mock_on_commit = mocker.patch("klasses.signals.on_commit")
    personal_price = PersonalPriceFactory.create()
    prev_call_count = mock_on_commit.call_count
    personal_price.delete()
    assert mock_on_commit.call_count == prev_call_count + 1
    # Test the function call from the signal handler
    patched_adjust_app = mocker.patch("klasses.signals.adjust_app_state_for_new_price")
    personal_price_post_delete(mocker.Mock(), personal_price)
    # Call the function that was passed into "on_commit", which in this case should be our patched API function
    mock_on_commit.call_args[0][0]()
    patched_adjust_app.assert_called_once_with(
        user=personal_price.user, bootcamp_run=personal_price.bootcamp_run
    )
