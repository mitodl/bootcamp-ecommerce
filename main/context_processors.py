"""
context processors for bootcamp
"""
from django.conf import settings

# pylint: disable=unused-argument


def api_keys(request):
    """
    Pass a `APIKEYS` dictionary into the template context, which holds
    IDs and secret keys for the various APIs used in this project.
    """
    return {
        "APIKEYS": {
            "GOOGLE_ANALYTICS": settings.GA_TRACKING_ID,
            "SMARTLOOK": settings.SL_TRACKING_ID,
            "GOOGLE_TAG_MANAGER": settings.GTM_TRACKING_ID,
        }
    }


def configuration_context(request):
    """
    Configuration context for django templates
    """
    return {
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG.get("HELP_WIDGET_ENABLED"),
            "help_widget_key": settings.ZENDESK_CONFIG.get("HELP_WIDGET_KEY"),
        }
    }
