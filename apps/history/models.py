from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import TextField


class History(models.Model):
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    long_description = TextField()
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='histories'
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50)
    button_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'


