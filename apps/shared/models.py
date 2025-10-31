import uuid

from django.contrib.contenttypes.models import ContentType
from django.db import models


class Language(models.TextChoices):
    RU = "RU", "Russian"
    EN = "EN", "English"
    CRL = "CRL", "Cyrillic"
    UZ = "UZ", "Uzbek"


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamp fields
    """
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']