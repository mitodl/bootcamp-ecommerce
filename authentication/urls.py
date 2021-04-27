"""URL configurations for authentication"""
from django.contrib.auth import views as auth_views
from django.urls import path, include
from social_core.backends.email import EmailAuth

from authentication.views import (
    LoginEmailView,
    LoginPasswordView,
    RegisterEmailView,
    RegisterConfirmView,
    RegisterDetailsView,
    RegisterComplianceView,
    RegisterExtraDetailsView,
    get_social_auth_types,
    CustomDjoserAPIView,
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
    path(
        "api/password_reset/",
        CustomDjoserAPIView.as_view({"post": "reset_password"}),
        name="password-reset-api",
    ),
    path(
        "api/password_reset/confirm/",
        CustomDjoserAPIView.as_view({"post": "reset_password_confirm"}),
        name="password-reset-confirm-api",
    ),
    path(
        "api/set_password/",
        CustomDjoserAPIView.as_view({"post": "set_password"}),
        name="set-password-api",
    ),
    path("api/auths/", get_social_auth_types, name="get-auth-types-api"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
