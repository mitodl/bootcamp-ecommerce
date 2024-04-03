"""API functions for CMS"""

from django.template import engines
from django.template.base import VariableNode
from django.template.exceptions import TemplateSyntaxError


def render_template(text, *, context):
    """
    Render a template given its text. If there is a variable in the template which is not in the context,
    an exception will be raised to allow for a ValidationError to be raised upstream.

    Args:
        text (str): The text to be rendered
        context (dict): Template variables to fill in the template parameters
    """
    engine = engines["django"]
    template = engine.from_string(text)
    variable_names = {
        node.token.contents
        for node in template.template.nodelist
        if isinstance(node, VariableNode)
    }
    for name in variable_names:
        if name not in context:
            raise TemplateSyntaxError(f"Can't find a variable with name '{name}'")
    return template.render(context=context)
