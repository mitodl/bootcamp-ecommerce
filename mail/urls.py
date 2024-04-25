"""URL configurations for mail"""

from django.conf import settings
from django.urls import path

from mail.views import EmailDebuggerView

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        path("__emaildebugger__/", EmailDebuggerView.as_view(), name="email-debugger")
    ]
