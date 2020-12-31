""" Tests for cms pages. """

import json
import pytest

from django.http.response import Http404
from django.test import override_settings

from cms.factories import (
    SiteNotificationFactory,
    BootcampRunPageFactory,
    ResourcePageFactory,
    LearningResourceSectionFactory,
    ProgramDescriptionSectionFactory,
    HomeAlumniSectionFactory,
    HomePageFactory,
    CatalogGridSectionFactory,
    ThreeColumnImageTextSectionFactory,
    InstructorSectionFactory,
    AdmissionSectionFactory,
    CertificateIndexPageFactory,
    CertificatePageFactory,
)
from cms import models
from klasses.factories import BootcampRunCertificateFactory

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
    assert models.LearningResourceSection.can_create_at(bootcamp_run_page)
    learning_resources_page = LearningResourceSectionFactory.create(
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


def test_three_column_image_text_section_under_runpage():
    """
    Three column image text section subpage should provide expected values.
    """
    bootcamp_run_page = BootcampRunPageFactory.create()
    assert bootcamp_run_page.three_column_image_text_section is None
    assert models.ThreeColumnImageTextSection.can_create_at(bootcamp_run_page)
    three_column_image_text_section = ThreeColumnImageTextSectionFactory.create(
        column_image_text_section=json.dumps(
            [
                {
                    "type": "column_image_text_section",
                    "value": {
                        "heading": "heading of block",
                        "sub_heading": "subheading of block",
                        "body": "<p>body of the block</p>",
                        "image__title": "title of the image",
                    },
                }
            ]
        ),
        parent=bootcamp_run_page,
    )
    assert bootcamp_run_page.three_column_image_text_section
    assert (
        bootcamp_run_page.three_column_image_text_section
        == three_column_image_text_section
    )
    for (
        item
    ) in (
        three_column_image_text_section.column_image_text_section
    ):  # pylint: disable=not-an-iterable
        assert item.value.get("heading") == "heading of block"
        assert item.value.get("sub_heading") == "subheading of block"
        assert item.value.get("body").source == "<p>body of the block</p>"


def test_three_column_image_text_section_under_homepage():
    """
    Three column image text section subpage should provide expected values.
    """
    home_page = HomePageFactory.create()
    assert home_page.three_column_image_text_section is None
    assert models.ThreeColumnImageTextSection.can_create_at(home_page)
    three_column_image_text_section = ThreeColumnImageTextSectionFactory.create(
        column_image_text_section=json.dumps(
            [
                {
                    "type": "column_image_text_section",
                    "value": {
                        "heading": "heading of block",
                        "sub_heading": "subheading of block",
                        "body": "<p>body of the block</p>",
                        "image__title": "title of the image",
                    },
                }
            ]
        ),
        parent=home_page,
    )
    assert home_page.three_column_image_text_section
    assert home_page.three_column_image_text_section == three_column_image_text_section
    for (
        item
    ) in (
        three_column_image_text_section.column_image_text_section
    ):  # pylint: disable=not-an-iterable
        assert item.value.get("heading") == "heading of block"
        assert item.value.get("sub_heading") == "subheading of block"
        assert item.value.get("body").source == "<p>body of the block</p>"


def test_instructors_section():
    """
    Verify user can create instructor section under bootcamp run page.
    """
    bootcamp_run_page = BootcampRunPageFactory.create()
    assert bootcamp_run_page.three_column_image_text_section is None
    assert models.ThreeColumnImageTextSection.can_create_at(bootcamp_run_page)

    instructor_section = InstructorSectionFactory.create(
        parent=bootcamp_run_page,
        banner_image__title="title of the image",
        heading="heading",
        sections=json.dumps(
            [
                {
                    "type": "section",
                    "value": {
                        "heading": "Introduction",
                        "sub_heading": "Subheading",
                        "heading_singular": "Singular heading",
                        "members": {
                            "name": "Name",
                            "image__title": "Image title",
                            "title": "Title",
                        },
                    },
                }
            ]
        ),
    )
    assert bootcamp_run_page.instructors
    assert bootcamp_run_page.instructors == instructor_section


def test_admission_section():
    """
    Verify user can create admission section under bootcamp page but not HomePage.
    """
    bootcamp_run_page = BootcampRunPageFactory.create()
    home_page = HomePageFactory.create()
    assert bootcamp_run_page.admissions_section is None
    assert models.AdmissionsSection.can_create_at(bootcamp_run_page)
    assert models.AdmissionsSection.can_create_at(home_page) is False

    admission_section = AdmissionSectionFactory.create(
        parent=bootcamp_run_page,
        admissions_image__title="title of the image",
        notes="notes",
        details="details",
        bootcamp_format="bootcamp format",
        bootcamp_format_details="format details",
        dates="dates",
        dates_details="dates details",
        price=10,
        price_details="price details",
    )
    assert bootcamp_run_page.admissions_section
    assert bootcamp_run_page.admissions_section == admission_section


def test_program_description_page():
    """
    Verify user can create program description page.
    """
    page = ProgramDescriptionSectionFactory.create(
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


def test_home_alumni_page():
    """
    Verify user can create global alumni page under HomePage.
    """
    home_page = HomePageFactory.create()
    assert not home_page.alumni
    home_alumni_page = HomeAlumniSectionFactory.create(
        parent=home_page,
        banner_image__title="program-description-image",
        heading="heading of the page",
        text="text of the page",
        highlight_quote="quote of the page",
        highlight_name="ABC",
    )
    assert home_page.alumni == home_alumni_page
    assert home_alumni_page.heading == "heading of the page"
    assert home_alumni_page.text == "text of the page"
    assert home_alumni_page.highlight_quote == "quote of the page"
    assert home_alumni_page.highlight_name == "ABC"


def test_home_catalog():
    """
    Verify user can create catalog grid under home page
    """
    home = HomePageFactory()
    assert not home.catalog
    catalog = CatalogGridSectionFactory(parent=home)
    assert home.catalog == catalog


def test_certificate_for_bootcamp_run_page():
    """
    The Certificate property should return expected values if associated with a CertificatePage
    """
    bootcamp_run_page = BootcampRunPageFactory.create()
    assert models.CertificatePage.can_create_at(bootcamp_run_page)
    assert not models.SignatoryPage.can_create_at(bootcamp_run_page)

    certificate_page = CertificatePageFactory.create(
        parent=bootcamp_run_page,
        bootcamp_run_name="bootcamp_run",
        certificate_name="certificate_name",
        location="location",
        signatories__0__signatory__name="Name",
        signatories__0__signatory__title_1="Title_1",
        signatories__0__signatory__title_2="Title_2",
        signatories__0__signatory__organization="Organization",
        signatories__0__signatory__signature_image__title="Image",
    )
    assert certificate_page.get_parent() == bootcamp_run_page
    assert certificate_page.bootcamp_run_name == "bootcamp_run"
    assert certificate_page.certificate_name == "certificate_name"
    assert certificate_page.location == "location"
    for signatory in certificate_page.signatories:  # pylint: disable=not-an-iterable
        assert signatory.value.name == "Name"
        assert signatory.value.title_1 == "Title_1"
        assert signatory.value.title_2 == "Title_2"
        assert signatory.value.organization == "Organization"
        assert signatory.value.signature_image.title == "Image"


@override_settings(**{"FEATURES": {"ENABLE_CERTIFICATE_USER_VIEW": True}})
def test_certificate_index_page(rf):
    """
    test for certificate index page
    """
    home_page = HomePageFactory()
    assert models.CertificateIndexPage.can_create_at(home_page)

    certifcate_index_page = CertificateIndexPageFactory.create(parent=home_page)
    request = rf.get(certifcate_index_page.get_url())
    bootcamp_run_page = BootcampRunPageFactory.create()
    certificate = BootcampRunCertificateFactory.create(
        bootcamp_run=bootcamp_run_page.bootcamp_run
    )
    certificate_page = CertificatePageFactory.create(parent=bootcamp_run_page)
    request = rf.get(certificate_page.get_url())
    assert (
        certifcate_index_page.bootcamp_certificate(
            request, certificate.uuid
        ).status_code
        == 200
    )

    with pytest.raises(Http404):
        certifcate_index_page.bootcamp_certificate(
            request, "00000000-0000-0000-0000-000000000000"
        )

    # Revoke the certificate and check index page returns 404
    certificate.revoke()

    with pytest.raises(Http404):
        certifcate_index_page.bootcamp_certificate(request, certificate.uuid)

    with pytest.raises(Http404):
        certifcate_index_page.index_route(request)
