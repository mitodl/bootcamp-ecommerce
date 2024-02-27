from django import template

register = template.Library()

@register.simple_tag
def bootcamp_duration_format(start, end):
    """Returns the formatted date to be displayed on bootcamps cards"""
    if start.year == end.year and start.month == end.month:
        return f"{start.strftime('%B %d')} - {end.strftime('%d, %Y')}"
    elif start.year == end.year:
        return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
    else:
        return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"