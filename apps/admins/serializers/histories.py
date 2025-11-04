from django.utils import timezone
from rest_framework import serializers

from apps.history.models import History
from apps.shared.mixins.translation_mixins import TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin

class HistoryTranslationMixin:
    translatable_fields = ['title', 'short_description', 'long_description', 'button_text', 'images']
    media_fields = ['images']


class HistorySerializer(HistoryTranslationMixin, TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin,
                        serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = History
        fields = '__all__'
        extra_kwargs = {
            'button_link': {'required': False, 'allow_null': True, 'allow_blank': True},
            'is_active': {'required': False},
        }

    def validate_start_date(self, value):
        if self.instance is None:
            if value < timezone.now():
                raise serializers.ValidationError(
                    "Start date cannot be in the past"
                )
        return value

    def validate_end_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "End date cannot be in the past"
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date', self.instance.start_date if self.instance else None)
        end_date = attrs.get('end_date', self.instance.end_date if self.instance else None)
        if not start_date:
            raise serializers.ValidationError({
                'start_date': 'Start date is required'
            })

        if not end_date:
            raise serializers.ValidationError({
                'end_date': 'End date is required'
            })

        if start_date >= end_date:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date'
            })

        time_diff = end_date - start_date
        if time_diff.total_seconds() < 3600:  # 1 soat
            raise serializers.ValidationError({
                'end_date': 'History duration must be at least 1 hour'
            })

        button_text = attrs.get('button_text', self.instance.button_text if self.instance else None)
        button_link = attrs.get('button_link', self.instance.button_link if self.instance else None)

        if button_text and not button_link:
            raise serializers.ValidationError({
                'button_link': 'Button link is required when button text is provided'
            })

        return attrs

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Title must be at least 3 characters long"
            )
        return value.strip()

    def validate_short_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Short description must be at least 10 characters long"
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                "Short description cannot exceed 100 characters"
            )
        return value.strip()

    def validate_long_description(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError(
                "Long description must be at least 20 characters long"
            )
        return value.strip()

    def validate_button_text(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Button text must be at least 2 characters long"
            )
        if value and len(value) > 50:
            raise serializers.ValidationError(
                "Button text cannot exceed 50 characters"
            )
        return value.strip() if value else value

    def validate_button_link(self, value):
        if value:
            if not value.startswith(('http://', 'https://')):
                raise serializers.ValidationError(
                    "Button link must start with http:// or https://"
                )
        return value