"""
context processors for bootcamp
"""

import json

from django.conf import settings
from mitol.common.utils import webpack_public_path

from cms.utils import get_resource_page_urls


def api_keys(request):  # pylint: disable=unused-argument
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


def js_settings(request):
    """Context with JS settings"""
    return {
        "js_settings_json": json.dumps(
            {
                "release_version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "sentry_dsn": settings.SENTRY_DSN,
                "public_path": webpack_public_path(request),
                "zendesk_config": {
                    "help_widget_enabled": settings.ZENDESK_CONFIG.get(
                        "HELP_WIDGET_ENABLED"
                    ),
                    "help_widget_key": settings.ZENDESK_CONFIG.get("HELP_WIDGET_KEY"),
                },
                "recaptchaKey": settings.RECAPTCHA_SITE_KEY,
                "upload_max_size": settings.MAX_FILE_UPLOAD_MB * 1_000_000,
                "support_url": settings.SUPPORT_URL,
                "terms_url": get_resource_page_urls(request.site)["terms_of_service"],
                "novoed_base_url": settings.NOVOED_BASE_URL,
            }
        )
    }


def configuration_context(request):  # pylint: disable=unused-argument
    """
    Configuration context for django templates
    """
    return {
        "hubspot_portal_id": settings.HUBSPOT_CONFIG.get("HUBSPOT_PORTAL_ID"),
        "hubspot_footer_form_guid": settings.HUBSPOT_CONFIG.get(
            "HUBSPOT_FOOTER_FORM_GUID"
        ),
        "resource_page_urls": get_resource_page_urls(request.site),
        "support_url": settings.SUPPORT_URL,
        "zendesk_config": {
            "help_widget_enabled": settings.ZENDESK_CONFIG.get("HELP_WIDGET_ENABLED"),
            "help_widget_key": settings.ZENDESK_CONFIG.get("HELP_WIDGET_KEY"),
        },
    }
