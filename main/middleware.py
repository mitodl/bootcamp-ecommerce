""" Middleware classes for the main app"""
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class CachelessAPIMiddleware(MiddlewareMixin):
    """ Add Cache-Control header to API responses"""

    def process_response(self, request, response):
        """ Add a Cache-Control header to an API response """
        if request.path.startswith(settings.CACHEABLE_ENDPOINTS):
            response["Cache-Control"] = "max-age=3600, public"
        elif request.path.startswith("/api/"):
            response["Cache-Control"] = "private, no-store"
        return response
