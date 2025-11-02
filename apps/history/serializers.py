from rest_framework import serializers

from apps.history.models import History
from apps.shared.mixins.translation_mixins import TranslatedFieldsReadMixin


class HistoryTranslationMixin:
    translatable_fields = ['title', 'short_description', 'long_description', 'images']
    media_fields = ['images']


class HistoryListSerializer(HistoryTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
       model = History
       fields = ['title', 'short_description',
                 'button_text', 'button_link', 'created_at',
                 'updated_at', 'start_date', 'end_date'
                 ]


class HistoryRetrieveSerializer(HistoryTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['title', 'long_description',
                  'button_text', 'button_link', 'created_at',
                  'updated_at', 'start_date', 'end_date',
                  ]
