"""Templatetags for pycountry formatting"""
from django.template import Library
from django.template.defaultfilters import stringfilter
import pycountry

register = Library()


@stringfilter
def country_name(alpha_2):
    """
    Args:
        alpha_2(str): An IS-3166 alpha-2 country code
    Returns:
        str: The country name
    """
    country = pycountry.countries.get(alpha_2=alpha_2)
    return country.name if country else ""


register.filter(country_name)


@stringfilter
def state_or_territory_name(code):
    """
    Args:
        code(str): An IS-3166-2 subdivision (state or territory) code
    Returns:
        str: The state or territory name
    """
    state_or_territory = pycountry.subdivisions.get(code=code)
    return state_or_territory.name if state_or_territory else ""


register.filter(state_or_territory_name)
