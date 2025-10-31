from django.db import models
from django.db.models import TextField


class History(models.Model):
    title = models.CharField(max_length=100)
    short_description = models.CharField(max_length=100)
    long_description = TextField()
    image = models.ImageField(upload_to='histories/')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    button_text = models.CharField(max_length=50, default='Подробнее', verbose_name='Tugma matni')
    button_link = models.URLField(blank=True, null=True, verbose_name='Tugma havolasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'


