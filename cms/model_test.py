""" Tests for cms pages. """

import pytest

from cms.factories import SiteNotificationFactory

pytestmark = [pytest.mark.django_db]


def test_notification_snippet():
    """
    Verify that user can create site notification using cms.
    """
    message_text = "<p>hello this is a test notification</p>"
    notification = SiteNotificationFactory(message=message_text)

    assert str(notification) == message_text
