"""Templatetags for date parsing"""
import dateutil.parser
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@stringfilter
def parse_iso_datetime(date_string):
    """
    Args:
        date_string (str): An ISO 8601-formatted datetime string
    Returns:
        datetime.datetime: The parsed datetime or None if the string formatting is invalid
    """
    try:
        return dateutil.parser.parse(date_string)
    except ValueError:
        return None


register.filter(parse_iso_datetime)
