import uuid

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

User = get_user_model()

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


class Media(BaseModel):
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    file = models.FileField(upload_to='%Y/%m/%d/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES)
    file_size = models.PositiveIntegerField(help_text="Size in bytes")
    mime_type = models.CharField(max_length=100)
    original_filename = models.CharField(max_length=255)

    # Generic relation - can attach to any model
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE,
        null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Metadata
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
    )
    is_public = models.BooleanField(default=False)
    language = models.CharField(
        max_length=3,
        choices=Language.choices,
        null=True, blank=True
    )

    class Meta:
        db_table = 'media'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['uploaded_by', 'created_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.media_type})"

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size

            if hasattr(self.file.file, 'content_type'):
                self.mime_type = self.file.file.content_type
            else:
                self.mime_type = 'application/octet-stream'

        super().save(*args, **kwargs)
