import uuid
from urllib.parse import quote

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from lux_clothing_service import settings
from user.models import EmailConfirmation, PasswordResetToken
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)
from dj_rest_auth.registration.views import RegisterView

from django.contrib.auth import logout, get_user_model
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.http import JsonResponse


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        try:
            user = super().save_user(request, user, form, commit=False)

            if not user.pk:
                user.save()

            EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"verified": False, "primary": True},
            )
        except ValidationError as e:
            raise ValidationError(f"Validation error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error: {str(e)}")

        return user

    def send_confirmation_mail(self, request, user, signup):
        with transaction.atomic():
            emailconfirmation = EmailConfirmation(user=user)
            emailconfirmation.save()

        activate_url = (
            f"{request.scheme}://{request.get_host()}/api/user/registration/account-confirm-email/"
            f"{quote(str(emailconfirmation.key))}/"
        )
        context = {
            "user": emailconfirmation.user,
            "activate_url": activate_url,
            "current_site": request.get_host(),
            "site_name": "Lux Clothing Portal",
        }

        self.send_mail(
            settings.ACCOUNT_EMAIL_TEMPLATE_PREFIX,
            emailconfirmation.user.email,
            context,
        )

    def confirm_email(self, request, email_address):
        user = email_address.user
        user.email_verified = True
        user.save()

    def respond_email_verification_sent(self, request, user):
        return JsonResponse(
            {"detail": "Email verification sent. Please confirm your email."}
        )

    def respond_email_confirm(self, request, email_address):
        if email_address.verified:
            return JsonResponse({"detail": "Email already verified."})
        email_address.verified = True
        email_address.save()
        return JsonResponse({"detail": "Email successfully verified."})


class CustomConfirmEmailView(APIView):
    """
    Class for confirming the user's email.
    Supports GET to confirm the email by key,
    and POST to resend the email confirmation.
    """

    def get(self, request, key, *args, **kwargs):
        try:
            uuid_obj = uuid.UUID(key)
        except ValueError:
            return JsonResponse(
                {"detail": "Invalid confirmation key format."}, status=400
            )

        try:
            confirmation = EmailConfirmation.objects.get(key=key)

            if confirmation.user.email_verified:
                return JsonResponse({"detail": "Email already verified."})

            confirmation.confirm()
            return JsonResponse({"detail": "Email successfully verified."})

        except EmailConfirmation.DoesNotExist:
            return JsonResponse({"detail": "Invalid confirmation key."}, status=400)
        except ValueError as e:
            return JsonResponse({"detail": str(e)}, status=400)


class ResendConfirmationThrottle(UserRateThrottle):
    rate = settings.RESEND_EMAIL_CONFIRMATION_THROTTLE


class ResendEmailConfirmationView(APIView):
    """
    Resending the email confirmation message.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ResendConfirmationThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Get the user by email
            user = get_user_model().objects.get(email=email)

            if user.email_verified:
                return Response(
                    {"detail": "Email is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Remove all old confirmations for this user
            user.emailconfirmation_set.all().delete()

            # Create a new confirmation
            adapter = CustomAccountAdapter()
            adapter.send_confirmation_mail(request, user, signup=False)

            return Response(
                {"detail": "Email confirmation sent."}, status=status.HTTP_200_OK
            )

        except get_user_model().DoesNotExist:
            return Response(
                {"detail": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class CreateUserView(RegisterView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            return response
        except Exception as e:
            raise e

    def perform_create(self, serializer):
        user = serializer.save()

        EmailAddress.objects.create(
            user=user,
            email=user.email,
            verified=False,
            primary=True,
        )
        adapter = CustomAccountAdapter()
        adapter.send_confirmation_mail(self.request, user, signup=True)

        return user


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutUserView(APIView):
    def get(self, request):
        token = Token.objects.get(user=request.user)
        token.delete()
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)


class RequestPasswordResetThrottle(UserRateThrottle):
    rate = settings.RESET_PASSWORD_THROTTLE


class RequestPasswordResetView(APIView):
    """
    Endpoint for requesting a password reset email.
    """

    throttle_classes = [RequestPasswordResetThrottle]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            # Don't show if user exist
            return Response(
                {"detail": "If this email exists, a reset link will be sent."},
                status=status.HTTP_200_OK,
            )

        token = PasswordResetToken.objects.create(user=user)
        reset_url = f"{request.scheme}://{request.get_host()}/api/user/reset-password/{token.token}/"

        # Render HTML-template
        subject = "Password Reset Request"
        context = {
            "user": user,
            "reset_url": reset_url,
        }
        html_message = render_to_string(
            "account/email/password_reset_email.html", context
        )

        send_mail(
            subject,
            "",
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=html_message,
        )

        return Response(
            {"detail": "If this email exists, a reset link will be sent."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    """
    Endpoint for resetting the password using a token.
    """

    permission_classes = [AllowAny]

    def post(self, request, token, *args, **kwargs):
        new_password = request.data.get("new_password")
        if not new_password:
            return Response(
                {"detail": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reset_token.is_valid():
            reset_token.delete()
            return Response(
                {"detail": "Token has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user password
        user = reset_token.user
        user.password = make_password(new_password)
        user.save()

        # Delete used token
        reset_token.delete()

        return Response(
            {"detail": "Password reset successful."}, status=status.HTTP_200_OK
        )
