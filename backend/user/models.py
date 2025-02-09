from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
)
from django.utils.timezone import now
from django.utils.translation import gettext as _

import uuid
from django.db import models

from lux_clothing_service import settings


class EmailConfirmation(models.Model):
    objects = models.Manager()
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)

    def confirm(self):
        if self.confirmed:
            raise ValueError("Email is already confirmed")

        self.confirmed = True
        self.save()
        self.user.email_verified = True
        self.user.save()

    def __str__(self):
        return f"Confirmation for {self.user.email}"


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    email_verified = models.BooleanField(default=False)
    primary_email = models.BooleanField(default=True)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


class PasswordResetToken(models.Model):
    objects = models.Manager()
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Token validation time
        return now() < self.created_at + settings.RESET_PASSWORD_TOKEN_VALIDATION_TIME
