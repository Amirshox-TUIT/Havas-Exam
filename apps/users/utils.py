import random
import string
import secrets
from datetime import timedelta
from django.utils import timezone


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


