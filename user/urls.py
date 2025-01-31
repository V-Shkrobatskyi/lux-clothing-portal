from dj_rest_auth.registration.views import VerifyEmailView
from django.urls import path
from user.views import (
    CreateUserView,
    ManageUserView,
    LogoutUserView,
    CreateTokenView,
    CustomConfirmEmailView,
    ResendEmailConfirmationView,
    RequestPasswordResetView,
    ResetPasswordView,
)

app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutUserView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path(
        "registration/account-confirm-email/<str:key>/",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    path(
        "registration/verify-email/",
        VerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    path(
        "resend-confirmation/",
        ResendEmailConfirmationView.as_view(),
        name="resend_email_confirmation",
    ),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path(
        "reset-password/<uuid:token>/",
        ResetPasswordView.as_view(),
        name="reset-password",
    ),
]
