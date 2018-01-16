""" Custom negotiation classes for REST framework """
from rest_framework.negotiation import BaseContentNegotiation


class IgnoreClientContentNegotiation(BaseContentNegotiation):
    """
    Ignore whatever a request's 'Accept' header is if any.
    """
    def select_parser(self, request, parsers):
        """
        Select the first parser in the `.parser_classes` list.

        Args:
            request(Request): The request to process
            parsers(list): list of parsers

        Returns:
            Parser: the parser to use (first in list)
        """
        return parsers[0]

    def select_renderer(self, request, renderers, format_suffix=None):
        """
        Select the first renderer in the `.renderer_classes` list.

        Args:
            request(Request): The request to process
            renderers(list): list of renderers
            format_suffix(string): not used

        Returns:
            Renderer: the renderer class to use (first in list)
        """
        return renderers[0], renderers[0].media_type
