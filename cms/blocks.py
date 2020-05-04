"""
Wagtail custom blocks for the CMS
"""
from wagtail.core import blocks


class ResourceBlock(blocks.StructBlock):
    """
    A custom block for resource pages.
    """

    heading = blocks.CharBlock(max_length=100)
    detail = blocks.RichTextBlock()
