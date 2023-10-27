"""
Wagtail custom blocks for the CMS
"""
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.blocks import StructValue


class ResourceBlock(blocks.StructBlock):
    """
    A custom block for resource pages.
    """

    heading = blocks.CharBlock(max_length=100)
    detail = blocks.RichTextBlock()


class InstructorBlock(blocks.StructBlock):
    """
    Block class that defines a instructor or sponsor
    """

    name = blocks.CharBlock(max_length=100, help_text="Name of the instructor/sponsor.")
    image = ImageChooserBlock(
        help_text="Profile image size must be at least 300x300 pixels."
    )
    title = blocks.CharBlock(
        max_length=255, help_text="A brief description about the instructor/sponsor."
    )


class InstructorSponsorItems(StructValue):
    """Custom value for StructBlock so that it can return Instructors or Sponsors"""

    def instructor_sponsor_items(self):
        """Return possible items for Instructors or Sponsors to be displayed to the user"""
        return self.get("members") or self.get("sponsors")


class InstructorSponsorBlock(blocks.StructBlock):
    """Parent Block class for sponsors and instructors"""

    heading = blocks.CharBlock(
        max_length=255, help_text="The heading to display for this section on the page."
    )
    subhead = blocks.RichTextBlock(
        help_text="The subhead to display for this section on the page."
    )
    heading_singular = blocks.CharBlock(
        max_length=100,
        help_text="Heading that will highlight the instructor or sponsor point.",
    )

    class Meta:
        value_class = InstructorSponsorItems


class InstructorSectionBlock(InstructorSponsorBlock):
    """
    Block class that defines an instrcutor section
    """

    members = blocks.StreamBlock(
        [("member", InstructorBlock())],
        help_text="The instructors to display in this section",
    )


class SponsorSectionBlock(InstructorSponsorBlock):
    """
    Block class that defines a sponsor section
    """

    sponsors = blocks.StreamBlock(
        [("sponsor", InstructorBlock())],
        help_text="The sponsors to display in this section",
    )


class ThreeColumnImageTextBlock(blocks.StructBlock):
    """
    A generic custom block used to input heading, sub-heading, body and image.
    """

    heading = blocks.CharBlock(
        max_length=100, help_text="Heading that will highlight the main point."
    )
    sub_heading = blocks.CharBlock(max_length=250, help_text="Area sub heading.")
    body = blocks.RichTextBlock()
    image = ImageChooserBlock(help_text="image size must be at least 150x50 pixels.")

    class Meta:
        icon = "plus"


class AlumniBlock(blocks.StructBlock):
    """
    Block class that defines alumni section
    """

    image = ImageChooserBlock(help_text="The image of the alumni")
    name = blocks.CharBlock(max_length=100, help_text="Name of the alumni.")
    title = blocks.CharBlock(
        max_length=255, help_text="The title to display after the name."
    )
    class_text = blocks.CharBlock(
        max_length=100, help_text="A brief description about the alumni class."
    )
    quote = blocks.RichTextBlock(
        help_text="The quote that appears on the alumni section."
    )


class TitleLinksBlock(blocks.StructBlock):
    """
    Block class that contains learning resources
    """

    title = blocks.CharBlock(
        max_length=100, help_text="The title to display for this section on the page."
    )
    links = blocks.RichTextBlock(
        help_text="Represent resources with the links to display. Add each link in the new line of the editor."
    )


class TitleDescriptionBlock(blocks.StructBlock):
    """
    A generic custom block used to input title and description.
    """

    title = blocks.CharBlock(
        max_length=100, help_text="Title that will highlight the main point."
    )
    description = blocks.RichTextBlock()

    class Meta:
        icon = "plus"


class CatalogSectionBootcampBlock(blocks.StructBlock):
    """
    Block that encapsulates a bootcamp run to be shown on the home page in catalog section.
    """

    page = blocks.PageChooserBlock(
        "cms.BootcampRunPage", help_text="The bootcamp run to display"
    )
    format = blocks.CharBlock(
        max_length=128, help_text="The bootcamp format to display, e.g. Online Bootcamp"
    )
    application_deadline = blocks.DateTimeBlock(
        help_text="The application deadline to display for this bootcamp run"
    )
