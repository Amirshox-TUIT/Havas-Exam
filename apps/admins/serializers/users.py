from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.users.models.device import Device

User = get_user_model()


class UsersListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    device_type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'phone', 'device_type', 'last_login', 'date_joined', 'is_active')

    def get_full_name(self, obj):
        full_name = ""
        if obj.first_name:
            full_name += obj.first_name + " "

        if obj.last_name:
            full_name += obj.last_name + " "

        if obj.surname:
            full_name += obj.surname + " "

        return full_name if full_name != "" else "Unknown"

    def get_device_type(self, obj):
        device = obj.devices.first()
        return device.device_model if device else 'Unknown'


class InlineDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['device_model', 'ip_address', 'last_login']


class UserDetailSerializer(serializers.ModelSerializer):
    devices = InlineDeviceSerializer(many=True, read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'date_joined', 'devices']

    def get_full_name(self, obj):
        full_name = ""
        if obj.first_name:
            full_name += obj.first_name

        if obj.last_name:
            full_name += " " + obj.last_name

        if obj.surname:
            full_name += " " + obj.surname

        return full_name if full_name != "" else "Unknown"


class UserStatisticsSerializer(serializers.ModelSerializer):
    device_type = serializers.SerializerMethodField()
    all_users_count = serializers.SerializerMethodField()
    android_users_count = serializers.SerializerMethodField()
    ios_users_count = serializers.SerializerMethodField()
    online_users_count = serializers.SerializerMethodField()
    offline_users_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['device_type', 'phone', 'date_joined', 'all_users_count',
                  'android_users_count', 'ios_users_count',
                  'online_users_count', 'offline_users_count']

    def get_device_type(self, obj):
        device = obj.devices.first()
        return device.device_model if device else 'Unknown'
