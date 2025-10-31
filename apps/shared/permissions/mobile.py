
from rest_framework.permissions import BasePermission

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import Device


class IsMobileUser(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('Token')
        if not token:
            raise CustomException(message_key="TOKEN_IS_NOT_PROVIDED")

        device = Device.objects.filter(device_token=token).first()
        if not device:
            raise CustomException(message_key="DEVICE_NOT_FOUND")

        request.device = device
        return True


class IsAuthenticatedOrMobileUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_authenticated) or
            getattr(request, 'is_mobile', False)
        )