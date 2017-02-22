"""
bootcamp views
"""
import json

from django.conf import settings
from django.shortcuts import render
from raven.contrib.django.raven_compat.models import client as sentry

from bootcamp.templatetags.render_bundle import public_path
from bootcamp.utils import webpack_dev_server_host


def index(request):
    """
    The index view. Display available programs
    """

    js_settings = {
        "gaTrackingID": settings.GA_TRACKING_ID,
        'reactGaDebug': settings.REACT_GA_DEBUG,
        "host": webpack_dev_server_host(request),
        'edx_base_url': settings.EDXORG_BASE_URL,
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": sentry.get_public_dsn(),
        'support_email': settings.EMAIL_SUPPORT,
        'public_path': public_path(request),
    }

    return render(request, "bootcamp/index.html", context={
        "js_settings_json": json.dumps(js_settings),
    })
