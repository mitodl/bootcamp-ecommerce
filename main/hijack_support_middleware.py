from django.utils.deprecation import MiddlewareMixin


class HijackSupportMiddleware(MiddlewareMixin):
    """Middleware to support HijackMiddleware"""

    def process_request(self, request):
        """
        HijackMiddleware needs the session to be in accessed state in order to work properly.
        However, It doesn't work properly with our current architecture and django-hijack implementation
        because when the request reaches HijackMiddleware the session is not in accessed state.

        This middleware is written to ensure that the request session has accessed=True when the request reaches HijackMiddleware.

        We will probably need to add a more robust solution to django-hijack package."""
        if hasattr(request, "session"):
            request.session.get("hijack_history", [])
