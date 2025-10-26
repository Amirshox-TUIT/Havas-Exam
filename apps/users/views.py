from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneOTP
from .serializers import VerifySerializer, AuthSerializer
from .utils import generate_password, generate_6_digit_code, expiry_in_minutes, generate_username
from django.contrib.auth import get_user_model

from ..shared.utils.custom_response import CustomResponse

User = get_user_model()

EXPIRATION_MINUTES = 2
MAX_ATTEMPTS = 10


class AuthAPIView(APIView):
    serializer_class = AuthSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user_exists = User.objects.filter(phone=phone).exists()

        if not user_exists:
            user = User.objects.create(
                phone=phone,
                username=generate_username(),
                password=generate_password(),
                is_active=False
            )
            created = True

        else:
            created = False

        PhoneOTP.objects.filter(phone=phone, used=False).delete()
        code = generate_6_digit_code()
        expires_at = expiry_in_minutes(EXPIRATION_MINUTES)
        PhoneOTP.objects.create(
            phone=phone,
            code=code,
            expires_at=expires_at
        )

        data = {
            "phone": phone,
            "code": code,
            "expires_in_minutes": EXPIRATION_MINUTES,
            "max_attempts": MAX_ATTEMPTS,
        }

        message_key = "USER_CREATED" if created else "OTP_SENT"

        return CustomResponse.success(
            request=request,
            message_key=message_key,
            data=data,
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class VerifyCodeAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]

        otp = PhoneOTP.objects.filter(phone=phone, used=False).order_by('-created_at').first()
        if not otp:
            return CustomResponse.error(
                message_key='CODE_NOT_FOUND',
                context={'phone': phone},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expired():
            otp.delete()
            return CustomResponse.error(
                message_key='CODE_EXPIRED',
                context={'phone': phone},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if otp.attempts >= MAX_ATTEMPTS:
            return CustomResponse.error(
                message_key='TOO_MANY_ATTEMPTS',
                context={'phone': phone},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )

        if otp.code == str(code).zfill(6):
            otp.used = True
            otp.save()

            user = get_object_or_404(User, phone=phone)
            tokens = user.generate_jwt_tokens()
            user.is_active = True
            user.save()

            return CustomResponse.success(
                request=request,
                message_key='PHONE_VERIFIED',
                data={
                    'detail': 'Phone verified successfully',
                    'phone': phone,
                    'tokens': tokens
                },
                status_code=status.HTTP_200_OK,
            )

        otp.attempts += 1
        otp.save()
        remaining = MAX_ATTEMPTS - otp.attempts

        return CustomResponse.error(
            message_key='INVALID_CODE',
            context={'remaining_attempts': remaining},
            status_code=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return CustomResponse.success(
                message_key="SUCCESS_MESSAGE",
                request=request,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return CustomResponse.error(
                message_key="INVALID_TOKEN",
                context={"details": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )