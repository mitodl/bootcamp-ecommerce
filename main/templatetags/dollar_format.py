"""Templatetags for dollar value formatting"""
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@stringfilter
def dollar_format(dollars):
    """
    Args:
        dollars: A dollar value (Any value that can be turned into a float can be used - int, Decimal, str, etc.)
    Returns:
        str: The formatted string
    """
    return "${:,.2f}".format(float(dollars))


register.filter(dollar_format)
