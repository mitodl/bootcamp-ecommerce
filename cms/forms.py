"""Forms for CMS"""
from django.core.exceptions import ValidationError
from django.template.exceptions import TemplateSyntaxError
from wagtail.admin.forms import WagtailAdminPageForm

from cms.api import render_template
from cms.constants import SAMPLE_VARIABLES


class LetterTemplatePageForm(WagtailAdminPageForm):
    def clean_acceptance_text(self):
        """Validate that the templates are valid"""
        acceptance_text = self.cleaned_data["acceptance_text"]
        try:
            render_template(acceptance_text, context=SAMPLE_VARIABLES)
        except TemplateSyntaxError as ex:
            raise ValidationError(
                "Unable to render acceptance template text: %(exception)s",
                params={"exception": ex},
            )
        return acceptance_text

    def clean_rejection_text(self):
        rejection_text = self.cleaned_data["rejection_text"]
        try:
            render_template(rejection_text, context=SAMPLE_VARIABLES)
        except TemplateSyntaxError as ex:
            raise ValidationError(
                "Unable to render rejection template text: %(exception)s",
                params={"exception": ex},
            )
        return rejection_text
