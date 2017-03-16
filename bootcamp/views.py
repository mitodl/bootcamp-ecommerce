"""
bootcamp views
"""
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from raven.contrib.django.raven_compat.models import client as sentry

from bootcamp.templatetags.render_bundle import public_path


def index(request):
    """
    The index view. Display available programs
    """

    js_settings = {
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": sentry.get_public_dsn(),
        'public_path': public_path(request),
    }

    return render(request, "bootcamp/index.html", context={
        "js_settings_json": json.dumps(js_settings),
    })


@login_required
def pay(request):
    """
    View for the payment page
    """
    js_settings = {
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": sentry.get_public_dsn(),
        'public_path': public_path(request),
        'full_name': request.user.get_full_name(),
    }

    return render(request, "bootcamp/pay.html", context={
        "js_settings_json": json.dumps(js_settings),
    })
