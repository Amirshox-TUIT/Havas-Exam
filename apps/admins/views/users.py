from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAdminUser

from apps.admins.serializers.users import UsersListSerializer, UserDetailSerializer, UserStatisticsSerializer
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse
from apps.users.models.device import Device

User = get_user_model()


class UsersListAPIView(ListAPIView):
    queryset = User.objects.all()
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]
    serializer_class = UsersListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class UserDetailAPIView(RetrieveDestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)


class DeviceDestroyAPIView(RetrieveDestroyAPIView):
    queryset = Device.objects.all()
    permission_classes = [IsAdminUser]

    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        device = get_object_or_404(Device, id=self.kwargs['id'])
        if device and device.user != user:
            return CustomResponse.error(message_key='NOT_FOUND', status_code=status.HTTP_404_NOT_FOUND)
        return device

    def destroy(self, request, *args, **kwargs):
        device = self.get_object()
        device.logout()
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)

    
class UserStatisticsAPIView(ListAPIView):
    queryset = User.objects.filter(date_joined__gte=timezone.now())
    serializer_class = UserStatisticsSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        stats = {
            "all_users_count": User.objects.count(),
            "android_users_count": Device.objects.filter(device_type__icontains='ANDROID').count(),
            "ios_users_count": Device.objects.filter(device_type__icontains='IOS').count(),
            "online_users_count": User.objects.filter(is_active=True).count(),
            "offline_users_count": User.objects.filter(is_active=False).count(),
        }
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                "statistics": stats,
                "results": serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(
            data={
                "statistics": stats,
                "results": serializer.data
            },
            status_code=status.HTTP_200_OK
        )