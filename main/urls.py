"""
URLs for bootcamp
"""

from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from django.urls import re_path, include, path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.images.views.serve import ServeView

from main.views import react, BackgroundImagesCSSView, cms_login_redirect_view

root_urlpatterns = [re_path("", include(wagtail_urls))]

urlpatterns = (
    [
        re_path(r"^status/", include("server_status.urls")),
        re_path(r"^admin/", admin.site.urls),
        re_path(r"^hijack/", include("hijack.urls", namespace="hijack")),
        re_path("", include("applications.urls")),
        re_path("", include("ecommerce.urls")),
        re_path("", include("social_django.urls", namespace="social")),
        path("", include("authentication.urls")),
        path("", include("mail.urls")),
        path("", include("profiles.urls")),
        path("", include("klasses.urls")),
        re_path("", include("jobma.urls")),
        re_path(r"^logout/$", auth_views.LogoutView.as_view(), name="logout"),
        re_path(
            r"^background-images\.css$",
            BackgroundImagesCSSView.as_view(),
            name="background-images-css",
        ),
        # named routes mapped to the react app
        path("signin/", react, name="login"),
        path("signin/password/", react, name="login-password"),
        re_path(r"^signin/forgot-password/$", react, name="password-reset"),
        path(
            "signin/forgot-password/confirm/<slug:uid>/<slug:token>/",
            react,
            name="password-reset-confirm",
        ),
        re_path(
            r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
            ServeView.as_view(),
            name="wagtailimages_serve",
        ),
        path("create-account/", react, name="signup"),
        path("create-account/details/", react, name="signup-details"),
        path("create-account/retry/", react, name="signup-retry"),
        path("create-account/extra/", react, name="signup-extra"),
        path("create-account/denied/", react, name="signup-denied"),
        path("create-account/error/", react, name="signup-error"),
        path("create-account/confirm/", react, name="register-confirm"),
        path("account/inactive/", react, name="account-inactive"),
        path("account/confirm-email/", react, name="account-confirm-email-change"),
        path("account-settings/", react, name="account-settings"),
        path("applications/", react, name="applications"),
        path(
            "applications/<int:application_id>/payment-history/",
            react,
            name="application-history",
        ),
        re_path(r"^review/", react, name="review"),
        # Wagtail
        re_path(
            r"^images/([^/]*)/(\d*)/([^/]*)/[^/]*$",
            ServeView.as_view(),
            name="wagtailimages_serve",
        ),
        re_path(r"^cms/login", cms_login_redirect_view, name="wagtailadmin_login"),
        re_path(r"^cms/", include(wagtailadmin_urls)),
        re_path(r"^documents/", include(wagtaildocs_urls)),
        re_path(r"^idp/", include("djangosaml2idp.urls")),
    ]
    + root_urlpatterns
    + (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
)

handler404 = "main.views.page_404"
handler500 = "main.views.page_500"
