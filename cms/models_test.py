""" Tests for cms pages. """

import json
import pytest

from cms.factories import (
    SiteNotificationFactory,
    BootcampRunPageFactory,
    LearningResourcePageFactory,
)
from cms.models import LearningResourcePage

pytestmark = [pytest.mark.django_db]


def test_notification_snippet():
    """
    Verify that user can create site notification using cms.
    """
    message_text = "<p>hello this is a test notification</p>"
    notification = SiteNotificationFactory(message=message_text)

    assert str(notification) == message_text


def test_bootcamp_run_learning_resources():
    """
    Learning Resources subpage should provide expected values
    """
    bootcamp_run_page = BootcampRunPageFactory.create()
    assert bootcamp_run_page.learning_resources is None
    assert LearningResourcePage.can_create_at(bootcamp_run_page)
    learning_resources_page = LearningResourcePageFactory.create(
        parent=bootcamp_run_page,
        heading="heading",
        items=json.dumps(
            [{"type": "links", "value": {"title": "title", "links": "<p>links</p>"}}]
        ),
    )
    assert bootcamp_run_page.learning_resources
    assert bootcamp_run_page.learning_resources == learning_resources_page
    assert learning_resources_page.heading == "heading"
    for item in learning_resources_page.items:  # pylint: disable=not-an-iterable
        assert item.value.get("title") == "title"
        assert item.value.get("links") == "<p>links</p>"
