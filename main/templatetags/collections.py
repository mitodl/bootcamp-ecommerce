"""Template tags for collections of objects"""

from classytags.arguments import Argument, IntegerArgument
from classytags.core import Options
from classytags.helpers import AsTag
from django.template import Library

register = Library()


class CumulativeFieldTotal(AsTag):
    """Template tag for summing field values of a collection"""

    name = "cumulative_field_total"

    options = Options(
        Argument("items", required=True),
        Argument("field", required=True),
        IntegerArgument("offset", required=False),
        "as",
        Argument("varname", required=False, resolve=False),
    )

    def get_value(self, context, items, field, offset):  # noqa: ARG002
        """Sums up a field on a list of objects"""
        if offset is not None:
            items = items[:offset]
        return sum(item[field] for item in items)


register.tag(CumulativeFieldTotal)
