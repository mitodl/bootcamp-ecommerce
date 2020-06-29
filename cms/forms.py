"""Forms for CMS"""
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateSyntaxError
from wagtail.admin.forms import WagtailAdminPageForm

from cms.api import render_template
from cms.constants import SAMPLE_DECISION_TEMPLATE_CONTEXT


class LetterTemplatePageForm(WagtailAdminPageForm):
    """A form to do field validation of LetterTemplatePage"""

    def clean_acceptance_text(self):
        """Validate that the acceptance text is a valid Django template with no extra variables"""
        acceptance_text = self.cleaned_data["acceptance_text"]
        try:
            render_template(acceptance_text, context=SAMPLE_DECISION_TEMPLATE_CONTEXT)
        except TemplateSyntaxError as ex:
            raise ValidationError(
                "Unable to render acceptance template text: %(exception)s",
                params={"exception": ex},
            )
        return acceptance_text

    def clean_rejection_text(self):
        """Validate that the rejection text is a valid Django template with no extra variables"""
        rejection_text = self.cleaned_data["rejection_text"]
        try:
            render_template(rejection_text, context=SAMPLE_DECISION_TEMPLATE_CONTEXT)
        except TemplateSyntaxError as ex:
            raise ValidationError(
                "Unable to render rejection template text: %(exception)s",
                params={"exception": ex},
            )
        return rejection_text
