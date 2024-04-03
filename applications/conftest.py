"""Fixtures for applications"""

import pytest

from cms.factories import LetterTemplatePageFactory


@pytest.fixture(autouse=True)
def letter_template_page():
    """Create a LetterTemplatePage"""
    yield LetterTemplatePageFactory.create()
