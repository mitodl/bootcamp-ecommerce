""" Tests for main.middleware """
import pytest
from django.urls import reverse

from main.middleware import CachelessAPIMiddleware


@pytest.mark.parametrize(
    "view, cache_value",
    [["applications", None], ["applications_api-list", "private, no-store"]],
)
def test_cacheless_api_middleware(rf, view, cache_value):
    """Tests that the response has a cache-control header for API URLs"""
    request = rf.get(reverse(view))
    middleware = CachelessAPIMiddleware()
    assert (
        middleware.process_response(request, {}).get("Cache-Control", None)
        == cache_value
    )
