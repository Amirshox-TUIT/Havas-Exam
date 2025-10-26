from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models import PhoneOTP

User = get_user_model()

class AuthSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=14)

    def validate_phone(self, phone):
        if phone[0] != '+' or not phone[1:].isdigit() or not (10 < len(phone) < 15):
            raise CustomException(message_key='VALIDATION_ERROR', context={'phone': phone})
        return phone


class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ('code', 'phone')
