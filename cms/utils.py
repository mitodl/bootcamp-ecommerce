"""CMS utils"""
from cache_memoize import cache_memoize
from wagtail.core.models import Site

from cms.models import ResourcePagesSettings


# cache for an hour
@cache_memoize(60 * 60, args_rewrite=lambda site: [site.id])
def get_resource_page_urls(site):
    """
    Get resource page urls for a given site

    Args:
        site(wagtail.models.Site): the site to get resource pages for

    Returns:
        dict: the set of resource pages
    """
    site_page_settings = ResourcePagesSettings.for_site(site)
    pages = {
        "how_to_apply": site_page_settings.apply_page,
        "about_us": site_page_settings.about_us_page,
        "bootcamps_programs": site_page_settings.bootcamps_programs_page,
        "privacy_policy": site_page_settings.privacy_policy_page,
        "terms_of_service": site_page_settings.terms_of_service_page,
    }
    return {key: value.url if value else "" for key, value in pages.items()}


def invalidate_get_resource_page_urls():
    """
    Invalidate the cached values of get_resource_page_urls
    """
    for site in Site.objects.all():
        get_resource_page_urls.invalidate(site)
