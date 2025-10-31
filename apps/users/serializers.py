import datetime

from django.contrib.auth import get_user_model
from apps.users.models.user import PhoneOTP
from apps.users.models.device import Device
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models.device import AppVersion


User = get_user_model()

class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=14)
    password = serializers.CharField(max_length=128)

    def validate_phone(self, phone):
        if phone[0] != '+' or not phone[1:].isdigit() or not (10 < len(phone) < 15):
            raise CustomException(message_key='VALIDATION_ERROR', context={'phone': phone})
        return phone

    def validate_password(self, password):
        if len(password.strip()) < 8 or password.isdigit() or password.isalpha():
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password})
        return password


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=14)
    password = serializers.CharField(max_length=128)

    def validate_phone(self, phone):
        if phone[0] != '+' or not phone[1:].isdigit() or not (10 < len(phone) < 15):
            raise CustomException(message_key='VALIDATION_ERROR', context={'phone': phone})
        return phone

class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneOTP
        fields = ('code', 'phone')


class ProfileRetrieveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'surname', 'gender', 'birthday', 'phone')
        extra_kwargs = {
            'id': {'read_only': True},
            'phone': {'read_only': True},
        }

    def validate_first_name(self, fn):
        if fn == '':
            raise CustomException(message_key='VALIDATION_ERROR', context={'first_name': fn})
        return fn

    def validate_last_name(self, ln):
        if ln == '':
            raise CustomException(message_key='VALIDATION_ERROR', context={'last_name': ln})
        return ln

    def validate_surname(self, sn):
        if sn == '':
            raise CustomException(message_key='VALIDATION_ERROR', context={'surname': sn})
        return sn

    def validate_gender(self, gender):
        if gender != 'F' and gender != 'M':
            raise CustomException(message_key='VALIDATION_ERROR', context={'gender': gender})
        return gender

    def validate_birthday(self, birthday):
        if not isinstance(birthday, datetime.date) or birthday > datetime.date.today():
            raise CustomException(message_key='VALIDATION_ERROR', context={"birthday": birthday})
        return birthday


class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=14)

    def validate_phone(self, phone):
        if phone[0] != '+' or not phone[1:].isdigit() or not (10 < len(phone) < 15):
            raise CustomException(message_key='VALIDATION_ERROR', context={'phone': phone})
        return phone



class SetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    password_confirm = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, password):
        if len(password.strip()) < 8 or password.isdigit() or password.isalpha():
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password})
        return password

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password})
        return attrs


class UpdatePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    password1 = serializers.CharField(max_length=128, write_only=True)
    password2 = serializers.CharField(max_length=128, write_only=True)

    def validate_password(self, password):
        if len(password.strip()) < 8 or password.isdigit() or password.isalpha():
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password})
        return password

    def validate(self, attrs):
        password = attrs.get('password')
        password1 = attrs.get('password1')
        password2 = attrs.pop('password2')
        if password1 != password2 or password == password1:
            raise CustomException(message_key='VALIDATION_ERROR', context={'password': password1})
        return attrs



class DeviceRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = [
            'device_model', 'operation_version', 'device_type',
            'device_id', 'ip_address', 'app_version', 'firebase_token',
            'language', 'theme'
        ]
        extra_kwargs = {
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def validate_device_model(self, device_model):
        "iPhone <script>alert('xss')</script>"
        if 'script' in device_model:
            raise CustomException(message_key='NOT_CREATED')
        return device_model


class AppVersionSerializer(serializers.ModelSerializer):
    """Serializer for AppVersion model"""

    class Meta:
        model = AppVersion
        fields = [
            'id',
            'version',
            'device_type',
            'is_active',
            'force_update',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate data before saving"""
        # Validation is handled in model's clean() method
        # But we can add additional API-level validation here if needed
        return data


class AppVersionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AppVersion"""

    class Meta:
        model = AppVersion
        fields = [
            'version',
            'device_type',
            'is_active',
            'force_update',
            'description'
        ]

    def validate(self, attrs):
        version = attrs.get('version')
        device_type = attrs.get('device_type')

        app_version = AppVersion.objects.filter(version=version, device_type=device_type)
        if app_version.exists():
            raise CustomException(message_key="VERSION_ALREADY_EXISTS")
        return attrs


class AppVersionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating AppVersion"""

    class Meta:
        model = AppVersion
        fields = [
            'version',
            'is_active',
            'force_update',
            'description',
            'device_type'
        ]
        # All fields are optional for updates
        extra_kwargs = {
            'version': {'required': False},
            'is_active': {'required': False},
            'force_update': {'required': False},
            'description': {'required': False},
            'device_type': {'required': False},
        }


class ActiveVersionSerializer(serializers.ModelSerializer):
    """Simplified serializer for active versions"""

    class Meta:
        model = AppVersion
        fields = ['id', 'version', 'device_type', 'force_update']
