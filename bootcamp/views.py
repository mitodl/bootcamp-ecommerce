"""
bootcamp views
"""
import json

from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import render


def get_bundle_url(request, bundle_name):
    """
    Create a URL for the webpack bundle.
    """
    if settings.DEBUG and settings.USE_WEBPACK_DEV_SERVER:
        host = request.get_host().split(":")[0]

        return "{host_url}/{bundle}".format(
            host_url=settings.WEBPACK_SERVER_URL.format(host=host),
            bundle=bundle_name
        )
    else:
        return static("bundles/{bundle}".format(bundle=bundle_name))


def index(request):
    """
    The index view. Display available programs
    """

    host = request.get_host().split(":")[0]
    js_settings = {
        "gaTrackingID": settings.GA_TRACKING_ID,
        "host": host
    }

    return render(request, "bootcamp/index.html", context={
        "style_src": get_bundle_url(request, "style.js"),
        "root_src": get_bundle_url(request, "root.js"),
        "js_settings_json": json.dumps(js_settings),
    })
