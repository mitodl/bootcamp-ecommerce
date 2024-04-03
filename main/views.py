"""
bootcamp views
"""

import json

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from mitol.common.utils import has_all_keys


def is_cybersource_request(request):
    """
    Returns True if the request is a post-back from Cybersource after a payment was completed

    Args:
        request (django.http.request.HttpRequest): A request

    Returns:
        bool: True if the request is a post-back from Cybersource
    """
    return request.method == "POST" and has_all_keys(
        request.POST,
        {
            "decision",
            "signed_date_time",
            "req_merchant_defined_data4",
            "req_reference_number",
            "req_transaction_uuid",
        },
    )


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

    return render(request, "bootcamp/index.html")


@csrf_exempt
def react(request, **kwargs):
    """
    View for pages served by react
    """
    context = {}
    if is_cybersource_request(request):
        context["CSOURCE_PAYLOAD"] = json.dumps(
            {
                "decision": request.POST["decision"],
                "bootcamp_run_purchased": request.POST["req_merchant_defined_data4"],
                "purchase_date_utc": request.POST["signed_date_time"],
            }
        )
    else:
        context["CSOURCE_PAYLOAD"] = None
    return render(request, "bootcamp/react.html", context)


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
    response = render(request, template_filename)
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


def cms_login_redirect_view(request):
    """
    Redirects cms login page to site's login page
    """
    return redirect_to_login(reverse("wagtailadmin_home"), login_url=settings.LOGIN_URL)
