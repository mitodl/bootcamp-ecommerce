"""
bootcamp views
"""
import json

from django.conf import settings
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from main import features
from main.templatetags.render_bundle import public_path


def _serialize_js_settings(request):
    """
    Returns a dict of variables that are needed in the JS app. This dict is turned into a JS object.

    Returns:
        dict: A dict of JS app variables
    """
    return {
        "release_version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "sentry_dsn": settings.SENTRY_DSN,
        "public_path": public_path(request),
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG.get("HELP_WIDGET_ENABLED"),
            "help_widget_key": settings.ZENDESK_CONFIG.get("HELP_WIDGET_KEY"),
        },
        "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
        "support_url": settings.SUPPORT_URL,
    }


def get_base_context(request):
    """
    Returns the template context key/values needed for the base template and all templates that extend it

    Returns:
        dict: A dict of context variables to be used in a Django template
    """
    context = {
        "js_settings_json": json.dumps(_serialize_js_settings(request)),
        "resource_page_urls": {
            "how_to_apply": "/apply",
            "about_us": "/about-us",
            "bootcamps_programs": "/bootcamps-programs",
            "privacy_policy": "/privacy-policy",
        },
        "authenticated": not request.user.is_anonymous,
        "social_auth_enabled": features.is_enabled(features.SOCIAL_AUTH_API),
    }
    return context


@csrf_exempt
def index(request):
    """
    Index page
    """
    if request.user.is_authenticated:
        to_url = reverse("applications")
        if request.GET:
            to_url = "{}?{}".format(to_url, request.GET.urlencode())
        return redirect(to=to_url)

    return render(request, "bootcamp/index.html", context=get_base_context(request))


@csrf_exempt
def react(request, **kwargs):
    """
    View for pages served by react
    """
    return render(request, "bootcamp/react.html", context=get_base_context(request))


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
    response = render(
        request,
        template_filename,
        context={**get_base_context(request), "support_url": settings.SUPPORT_URL},
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
