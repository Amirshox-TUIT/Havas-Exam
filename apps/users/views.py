from rest_framework.generics import CreateAPIView, get_object_or_404, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PhoneOTP
from .serializers import VerifySerializer, RegisterSerializer, ProfileRetrieveUpdateSerializer, LoginSerializer, \
    ForgotPasswordSerializer, SetPasswordSerializer, UpdatePasswordSerializer
from .utils import generate_password, generate_6_digit_code, expiry_in_minutes, generate_username, register_device
from django.contrib.auth import get_user_model, authenticate

from ..shared.exceptions.custom_exceptions import CustomException
from ..shared.utils.custom_response import CustomResponse

User = get_user_model()

EXPIRATION_MINUTES = 2
MAX_ATTEMPTS = 10


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        user_exists = User.objects.filter(phone=phone).exists()

        if not user_exists:
            user = User.objects.create_user(
                phone=phone,
                username=generate_username(),
                password=password,
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
            register_device(request, user)

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



class LoginAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        password = serializer.validated_data['password']
        user = User.objects.filter(phone=phone).first()
        if not user:
            return CustomResponse.error(message_key='USER_NOT_FOUND', context={'phone': phone})
        username = user.username
        user = authenticate(request, username=username, password=password)
        if not user:
            return CustomResponse.error(message_key='INVALID_USER', context={'phone': phone})

        tokens = user.generate_jwt_tokens()
        user.is_active = True
        user.save()
        return CustomResponse.success(
            request=request,
            data={
                'detail': 'Phone verified successfully',
                'phone': phone,
                'tokens': tokens
            },
            status_code=status.HTTP_200_OK,
        )


class ForgotPasswordAPIView(APIView):
    serializer_class = ForgotPasswordSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        user_exists = User.objects.filter(phone=phone).exists()

        if not user_exists:
            return CustomResponse.error(message_key='USER_NOT_FOUND', context={'phone': phone})

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

        return CustomResponse.success(
            request=request,
            message_key="OTP_SENT",
            data=data,
            status_code=status.HTTP_200_OK
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


class SetPasswordAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SetPasswordSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        user = self.get_object()
        new_password = serializer.validated_data.get('password')
        user.set_password(new_password)
        user.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class UpdatePasswordAPIView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdatePasswordSerializer
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data['password']
        password1 = serializer.validated_data['password1']
        if not instance.check_password(password):
            return CustomResponse.error(message_key="VALIDATION_ERROR", context={"phone": instance.phone}, status_code=status.HTTP_400_BAD_REQUEST)

        instance.set_password(password1)
        instance.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class ProfileRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()
    serializer_class = ProfileRetrieveUpdateSerializer

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs, partial=True)