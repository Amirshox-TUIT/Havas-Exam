from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


class User(AbstractUser):
    phone = models.CharField(max_length=14, unique=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=(('M', 'Male'), ('F', 'Female')), null=True, blank=True)
    surname = models.CharField(max_length=20, null=True, blank=True)

    def generate_jwt_tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.surname}"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class DeviceModel(models.Model):
    DEVICE_CHOICES = (
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
        ('desktop', 'Desktop'),
        ('laptop', 'Laptop'),
        ('other', 'Other'),
    )

    OS_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('windows', 'Windows'),
        ('macos', 'macOS'),
        ('linux', 'Linux'),
        ('other', 'Other'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=255, unique=True, help_text="Unique device identifier")
    ip = models.GenericIPAddressField()
    device = models.CharField(max_length=10, choices=DEVICE_CHOICES, default='other')
    os = models.CharField(max_length=10, choices=OS_CHOICES, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True, help_text="Device model name")
    browser = models.CharField(max_length=50, null=True, blank=True)
    browser_version = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PhoneOTP(models.Model):
    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone} - {self.code}"



