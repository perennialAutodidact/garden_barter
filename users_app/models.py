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

    member_id = models.UUIDField(editable=False, unique=True, default=uuid.uuid1)

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


class Instructor(User):
    class Meta:
        verbose_name='Instructor'

class TeachingAssistant(User):
    
    class Meta:
        verbose_name='Teaching Assistant'


FUNDING_TYPE_CHOICES = {
    'selfpay': 'Self Pay',
    'vettec': 'VETTEC',
    'vrrap': 'VRRAP',
    'gi_bill': 'G.I. Bill',
    'voc_rehab': 'Vocational Rehab',
    'ch_33': 'Chapter 33',
    'worksource': 'Worksource',
    'not_specified': "Not Specified"
}

class FundingType(models.Model):
    title = models.CharField(max_length=20, choices=list(FUNDING_TYPE_CHOICES.items()))

    def __str__(self):
        return self.title

ENROLLMENT_CHOICES = {
    'PE': 'Pre-Enrollment',
    'EN': 'Enrolled: Not Started',
    'ES': 'Enrolled: Started',
    'EG': 'Enrolled: Graduated',
    'EP': 'Enrolled: Academic Probation',
    'EE': 'Enrolled: Expelled',
}

class EnrollmentStatus(models.Model):

    code = models.CharField(max_length=2, choices=list(ENROLLMENT_CHOICES.items()))

    def __str__(self):
        # Example output: EG - Enrolled: Graduated
        return f"{self.code} - {ENROLLMENT_CHOICES.get(self.code)}"


class Student(User):
    funding_type = models.ForeignKey('FundingType', on_delete=models.SET_NULL, null=True, related_name='students')
    enrollment_status = models.ForeignKey('EnrollmentStatus', on_delete=models.SET_NULL, null=True, related_name='students')
    paid_in_full = models.BooleanField(default=False)
    tuition_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    class Meta:
        verbose_name='Student'
        
    def __str__(self):
        return self.email

