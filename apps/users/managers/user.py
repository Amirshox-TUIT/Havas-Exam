
from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user manager that supports email, username, or phone_number authentication
    """

    def create_user(self, email=None, username=None, phone_number=None, password=None, **extra_fields):
        """
        Create and save a regular user
        """
        if not any([email, username, phone_number]):
            raise ValueError('User must have either email, username, or phone_number')

        # Normalize email if provided
        if email:
            email = self.normalize_email(email)

        # Create user instance
        user = self.model(
            email=email,
            username=username,
            phone_number=phone_number,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, username=None, phone_number=None, password=None, **extra_fields):
        """
        Create and save a superuser
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, username, phone_number, password, **extra_fields)

    def get_by_natural_key(self, username):
        """
        Allow authentication with email, username, or phone_number
        """
        return self.get(
            models.Q(email__iexact=username) |
            models.Q(username__iexact=username) |
            models.Q(phone_number=username)
        )
