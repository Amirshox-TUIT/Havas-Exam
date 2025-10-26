import random
import string
import secrets
from django.utils import timezone
from datetime import timedelta

import httpagentparser
from django.utils import timezone
from .models import DeviceModel


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def generate_username(prefix="user", length=6):
    letters_digits = string.ascii_lowercase + string.digits
    random_part = ''.join(random.choice(letters_digits) for _ in range(length))

    return f"{prefix}_{random_part}"

def generate_6_digit_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"

def expiry_in_minutes(minutes=2):
    return timezone.now() + timedelta(minutes=minutes)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_device_info(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed = httpagentparser.detect(user_agent)

    device = 'other'
    os = 'other'
    browser = None
    browser_version = None
    model = None
    if 'os' in parsed:
        os_name = parsed['os']['name'].lower()
        if 'android' in os_name:
            os = 'android'
            device = 'mobile'
        elif 'ios' in os_name:
            os = 'ios'
            device = 'mobile'
        elif 'windows' in os_name:
            os = 'windows'
            device = 'desktop'
        elif 'mac' in os_name:
            os = 'macos'
            device = 'laptop'
        elif 'linux' in os_name:
            os = 'linux'
            device = 'desktop'

    if 'browser' in parsed:
        browser = parsed['browser'].get('name')
        browser_version = parsed['browser'].get('version')

    return {
        'device': device,
        'os': os,
        'browser': browser,
        'browser_version': browser_version,
        'model': model,
    }


def register_device(request, user):
    from uuid import uuid4

    ip = get_client_ip(request)
    info = get_device_info(request)
    device_id = request.COOKIES.get('device_id', str(uuid4()))

    device, created = DeviceModel.objects.get_or_create(
        user=user,
        device_id=device_id,
        defaults={
            'ip': ip,
            'device': info['device'],
            'os': info['os'],
            'browser': info['browser'],
            'browser_version': info['browser_version'],
            'is_active': True,
        },
    )

    if not created:
        device.ip = ip
        device.last_login = timezone.now()
        device.is_active = True
        device.save(update_fields=['ip', 'last_login', 'is_active'])

    return device

