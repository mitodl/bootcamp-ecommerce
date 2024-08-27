"""URL configurations for authentication"""

from django.contrib.auth import views as auth_views
from django.urls import include, path
from social_core.backends.email import EmailAuth

from authentication.views import (
    LoginEmailView,
    LoginPasswordView,
    RegisterComplianceView,
    RegisterConfirmView,
    RegisterDetailsView,
    RegisterEmailView,
    RegisterExtraDetailsView,
    get_social_auth_types,
)

urlpatterns = [
    path("api/login/email/", LoginEmailView.as_view(), name="psa-login-email"),
    path("api/login/password/", LoginPasswordView.as_view(), name="psa-login-password"),
    # special case that's only available to email provider
    path(
        f"api/register/{EmailAuth.name}/email/",
        RegisterEmailView.as_view(),
        name="psa-register-email",
    ),
    path(
        "api/register/<slug:backend_name>/",
        include(
            [
                path(
                    "confirm/",
                    RegisterConfirmView.as_view(),
                    name="psa-register-confirm",
                ),
                path(
                    "details/",
                    RegisterDetailsView.as_view(),
                    name="psa-register-details",
                ),
                path(
                    "extra/",
                    RegisterExtraDetailsView.as_view(),
                    name="psa-register-extra",
                ),
                path(
                    "retry/",
                    RegisterComplianceView.as_view(),
                    name="psa-register-compliance",
                ),
            ]
        ),
    ),
    path("api/", include("mitol.authentication.urls.djoser_urls")),
    path("api/auths/", get_social_auth_types, name="get-auth-types-api"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
