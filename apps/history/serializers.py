from rest_framework import serializers

from apps.history.models import History
from apps.shared.utils.translation_serializer_mixin import TranslatableSerializerMixin


class HistoryListSerializer(TranslatableSerializerMixin):
    class Meta:
       model = History
       fields = ['title', 'short_description',
                 'image','button_text', 'button_link', 'created_at',
                 'updated_at', 'start_date', 'end_date'
                 ]


class HistoryRetrieveSerializer(TranslatableSerializerMixin):
    class Meta:
        model = History
        fields = ['title', 'long_description',
                  'image', 'button_text', 'button_link', 'created_at',
                  'updated_at', 'start_date', 'end_date',
                  ]
