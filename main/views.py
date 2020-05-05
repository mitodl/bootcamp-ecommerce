"""
bootcamp views
"""
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from main.templatetags.render_bundle import public_path
from main.serializers import serialize_maybe_user


def _serialize_js_settings(request):  # pylint: disable=missing-docstring
    return {
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": settings.SENTRY_DSN,
        "public_path": public_path(request),
        "user": serialize_maybe_user(request.user),
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG.get(
                "HELP_WIDGET_ENABLED"
            ),
            "help_widget_key": settings.ZENDESK_CONFIG.get("HELP_WIDGET_KEY"),
        },
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
    }


@csrf_exempt
def index(request):
    """
    Index page
    """
    if request.user.is_authenticated:
        to_url = reverse('pay')
        if request.GET:
            to_url = "{}?{}".format(to_url, request.GET.urlencode())
        return redirect(to=to_url)

    authenticated = not request.user.is_anonymous
    return render(request, "bootcamp/index.html", context={
        "js_settings_json": json.dumps(_serialize_js_settings(request)),
        "authenticated": authenticated,
    })


@login_required
@csrf_exempt
def react(request):
    """
    View for pages served by react
    """
    return render(request, "bootcamp/react.html", context={
        "js_settings_json": json.dumps(_serialize_js_settings(request)),
        "authenticated": not request.user.is_anonymous,
    })


class BackgroundImagesCSSView(TemplateView):
    """
    Pass a CSS file through Django's template system, so that we can make
    the URLs point to a CDN.
    """
    template_name = "background-images.css"
    content_type = "text/css"


def standard_error_page(request, status_code, template_filename):
    """
    Returns an error page with a given template filename and provides necessary context variables
    """
    authenticated = not request.user.is_anonymous
    response = render(
        request,
        template_filename,
        context={
            "js_settings_json": json.dumps(_serialize_js_settings(request)),
            "support_email": settings.EMAIL_SUPPORT,
            "authenticated": authenticated,
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
