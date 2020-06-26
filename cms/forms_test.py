"""Tests for CMS forms"""
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateSyntaxError
import pytest

from cms.factories import LetterTemplatePageFactory
from cms.forms import LetterTemplatePageForm


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def letter_template_page():
    """Create a LetterTemplatePage"""
    yield LetterTemplatePageFactory.create()


@pytest.mark.parametrize(
    "field_name, exception_message",
    [
        ["acceptance_text", "Unable to render acceptance template text: %(exception)s"],
        ["rejection_text", "Unable to render rejection template text: %(exception)s"],
    ],
)
def test_validation(mocker, field_name, exception_message):
    """The letter fields should raise a ValidationError if there is an exception"""
    exception = TemplateSyntaxError("uhoh")
    mocker.patch("cms.forms.render_template", side_effect=exception)
    mocked_form = mocker.Mock(cleaned_data={field_name: "text"})
    clean_field_name = f"clean_{field_name}"

    with pytest.raises(ValidationError) as ex:
        getattr(LetterTemplatePageForm, clean_field_name)(mocked_form)
    assert ex.value.args == (exception_message, None, {"exception": exception})
