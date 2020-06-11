""" Tests for cms pages. """

import json
import pytest

from cms.factories import (
    SiteNotificationFactory,
    BootcampRunPageFactory,
    ResourcePageFactory,
    LearningResourcePageFactory,
    ProgramDescriptionPageFactory,
    GlobalAlumniPageFactory,
    HomePageFactory,
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


def test_program_description_page():
    """
    Verify user can create program description page.
    """
    page = ProgramDescriptionPageFactory.create(
        statement="statement of the page",
        heading="heading of the page",
        body="body of the page",
        image__title="program-description-image",
        banner_image__title="program-description-banner-image",
        steps=json.dumps(
            [
                {
                    "type": "steps",
                    "value": {
                        "title": "Introduction",
                        "description": "description of title",
                    },
                }
            ]
        ),
    )
    assert page.statement == "statement of the page"
    assert page.heading == "heading of the page"
    assert page.body == "body of the page"

    for block in page.steps:  # pylint: disable=not-an-iterable
        assert block.block_type == "steps"
        assert block.value["title"] == "Introduction"
        assert block.value["description"].source == "description of title"


def test_bootcamp_run_page_site_name(settings, mocker):
    """
    BootcampRunPage should include site_name in its context
    """
    settings.SITE_NAME = "a site's name"
    page = BootcampRunPageFactory.create()
    assert page.get_context(mocker.Mock())["site_name"] == settings.SITE_NAME


def test_resource_page_site_name(settings, mocker):
    """
    ResourcePage should include site_name in its context
    """
    settings.SITE_NAME = "a site's name"
    page = ResourcePageFactory.create()
    assert page.get_context(mocker.Mock())["site_name"] == settings.SITE_NAME


def test_global_alumni_page():
    """
    Verify user can create global alumni page under HomePage.
    """
    home_page = HomePageFactory.create()
    assert not home_page.global_alumni
    global_alumni_page = GlobalAlumniPageFactory.create(
        parent=home_page,
        banner_image__title="program-description-image",
        heading="heading of the page",
        text="text of the page",
        highlight_quote="quote of the page",
        highlight_name="ABC",
    )
    assert home_page.global_alumni == global_alumni_page
    assert global_alumni_page.heading == "heading of the page"
    assert global_alumni_page.text == "text of the page"
    assert global_alumni_page.highlight_quote == "quote of the page"
    assert global_alumni_page.highlight_name == "ABC"
