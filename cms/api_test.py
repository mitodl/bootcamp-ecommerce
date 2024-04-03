"""Tests for CMS functions"""

from django.template.exceptions import TemplateSyntaxError
import pytest

from cms.api import render_template


TEMPLATE = "{{ x }}{{ y }}"
BROKEN_TEMPLATE = "{% x %}"
VARS = {"x": "a", "y": "b"}


def test_render_template():
    """render_template should fill in variables in a given template"""
    assert render_template(TEMPLATE, context=VARS) == "ab"


def test_render_template_broken():
    """A broken template should raise an error"""
    with pytest.raises(TemplateSyntaxError) as ex:
        render_template(BROKEN_TEMPLATE, context=VARS)

    assert "Invalid block tag" in ex.value.args[0]


def test_render_template_missing_vars():
    """A template referencing vars that aren't in the context should raise an error"""
    with pytest.raises(TemplateSyntaxError) as ex:
        render_template(TEMPLATE, context={})

    assert "Can't find a variable with name" in ex.value.args[0]
