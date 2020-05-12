"""
Wagtail custom blocks for the CMS
"""
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock


class ResourceBlock(blocks.StructBlock):
    """
    A custom block for resource pages.
    """

    heading = blocks.CharBlock(max_length=100)
    detail = blocks.RichTextBlock()


class InstructorBlock(blocks.StructBlock):
    """
    Block class that defines a instructor
    """

    name = blocks.CharBlock(
        max_length=100, help_text="Name of the instructor.")
    image = ImageChooserBlock(
        help_text="Profile image size must be at least 300x300 pixels."
    )
    title = blocks.CharBlock(
        max_length=255,
        help_text="A brief description about the instructor."
    )


class InstructorSectionBlock(blocks.StructBlock):
    """
    Block class that defines a instrcutors section
    """
    heading = blocks.CharBlock(
        max_length=255,
        help_text="The heading to display for this section on the page.",
    )
    subhead = blocks.CharBlock(
        max_length=255,
        help_text="The subhead to display for this section on the page.",
    )
    members = blocks.StreamBlock(
        [("member", InstructorBlock())],
        help_text="The instructors to display in this section",
    )
