"""Templatetags for dollar value formatting"""

from decimal import Decimal

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@stringfilter
def dollar_format(dollars):
    """
    Args:
        dollars (any): A dollar value (Any value that can be turned into a float can be used - int, Decimal, str, etc.)
    Returns:
        str: The formatted string
    """
    decimal_dollars = Decimal(dollars)
    if decimal_dollars < 0:
        return "-${:,.2f}".format(-decimal_dollars)
    else:
        return "${:,.2f}".format(decimal_dollars)


register.filter(dollar_format)
