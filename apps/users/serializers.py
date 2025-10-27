import datetime

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.shared.exceptions.custom_exceptions import CustomException
from apps.users.models import PhoneOTP

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



