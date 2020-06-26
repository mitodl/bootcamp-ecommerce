"""
bootcamp views
"""
from django.shortcuts import render, redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView


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
    return render(request, "bootcamp/react.html")


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
