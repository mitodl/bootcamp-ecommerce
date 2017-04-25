"""
bootcamp views
"""
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from raven.contrib.django.raven_compat.models import client as sentry

from bootcamp.templatetags.render_bundle import public_path
from bootcamp.serializers import serialize_maybe_user


def _serialize_js_settings(request):  # pylint: disable=missing-docstring
    return {
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": sentry.get_public_dsn(),
        "public_path": public_path(request),
        "user": serialize_maybe_user(request.user)
    }


def index(request):  # pylint: disable=missing-docstring
    if request.user.is_authenticated():
        return redirect(to='pay')
    return render(request, "bootcamp/index.html", context={
        "js_settings_json": json.dumps(_serialize_js_settings(request)),
    })


@login_required
def pay(request):
    """
    View for the payment page
    """
    return render(request, "bootcamp/pay.html", context={
        "js_settings_json": json.dumps(_serialize_js_settings(request)),
    })


def standard_error_page(request, status_code, template_filename):
    """
    Returns an error page with a given template filename and provides necessary context variables
    """
    response = render(
        request,
        template_filename,
        context={
            "js_settings_json": json.dumps(_serialize_js_settings(request)),
            "support_email": settings.EMAIL_SUPPORT,
        }
    )
    response.status_code = status_code
    return response


def page_404(request, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Overridden handler for the 404 error pages.
    """
    return standard_error_page(request, 404, "404.html")


def page_500(request, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Overridden handler for the 404 error pages.
    """
    return standard_error_page(request, 500, "500.html")
