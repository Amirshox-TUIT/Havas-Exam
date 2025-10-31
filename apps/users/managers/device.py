
from django.db import models
from django.utils import timezone


class DeviceManager(models.Manager):
    """Custom manager for Device model with business logic methods"""

    # Filter methods
    def active(self):
        """Get only active devices"""
        return self.filter(is_active=True)

    def for_user(self, user):
        """Get devices for a specific user"""
        return self.filter(user=user)

    def by_device_type(self, device_type):
        """Filter by device type"""
        return self.filter(device_type=device_type)

    def with_push_enabled(self):
        """Get devices with push notifications enabled"""
        return self.filter(is_push_notification=True)

    # Business logic methods
    def get_active_devices(self, user):
        """Get all active devices for a user, ordered by last login"""
        return self.filter(user=user, is_active=True).order_by('-last_login')

    def logout_all_devices(self, user):
        """Logout from all devices for a user"""
        return self.filter(user=user, is_active=True).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    def logout_other_devices(self, user, current_device_id):
        """Logout from all devices except current one"""
        return self.filter(
            user=user,
            is_active=True
        ).exclude(
            id=current_device_id
        ).update(
            is_active=False,
            logged_out_at=timezone.now()
        )

    def is_token_valid(self, refresh_token_jti):
        """Check if refresh token JTI is valid (device is active)"""
        return self.filter(
            refresh_token_jti=refresh_token_jti,
            is_active=True
        ).exists()

    def get_by_token(self, refresh_token_jti):
        """Get device by refresh token JTI"""
        return self.get(refresh_token_jti=refresh_token_jti)

    def create_device_session(self, user, device_data, refresh_token_jti):
        """
        Create a new device session

        Args:
            user: User instance
            device_data: Dict with device info (device_model, device_type, etc.)
            refresh_token_jti: JWT refresh token ID

        Returns:
            Device instance
        """
        return self.create(
            user=user,
            refresh_token_jti=refresh_token_jti,
            is_active=True,
            **device_data
        )
