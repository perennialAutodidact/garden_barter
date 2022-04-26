from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt # use on all sensitive fields (https://www.securecoding.com/blog/cryptography-for-security-in-django-app/)
import uuid

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError('The given email must be set')
        if not password:
            raise ValueError('Password cannot be blank')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={ # overwrite default error message for unique constraint
            'unique':"This email has already been registered."
        }
    )

    # optional username
    username = models.CharField(max_length=30, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

class RefreshToken(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='refresh_token')
    token = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user}'s refresh token"

