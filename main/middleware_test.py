""" Tests for main.middleware """
import pytest
from django.test import override_settings
from django.urls import reverse

from main.middleware import CachelessAPIMiddleware


@pytest.mark.parametrize(
    "view, cache_value, cacheable_endpoints_cache_value",
    [
        ["applications", None, "max-age=3600, public"],
        ["applications_api-list", "private, no-store", "max-age=3600, public"],
    ],
)
def test_cacheless_api_middleware(
    rf, view, cache_value, cacheable_endpoints_cache_value
):
    """Tests that the response has a cache-control header for API URLs"""
    request = rf.get(reverse(view))
    middleware = CachelessAPIMiddleware()
    assert (
        middleware.process_response(request, {}).get("Cache-Control", None)
        == cache_value
    )
    with override_settings(
        CACHEABLE_ENDPOINTS=(reverse(view),),
        CACHEABLE_ENDPOINTS_CACHE_VALUE=cacheable_endpoints_cache_value,
    ):
        request = rf.get(reverse(view))
        assert (
            middleware.process_response(request, {}).get("Cache-Control", None)
            == cacheable_endpoints_cache_value
        )
