from django.utils import translation
from rest_framework import serializers

class TranslatableSerializerMixin(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        lang = translation.get_language() or 'uz'

        translated_data = {}
        for field, value in data.items():
            translated_field_name = f"{field}_{lang}"
            if hasattr(instance, translated_field_name):
                translated_data[field] = getattr(instance, translated_field_name)
            else:
                translated_data[field] = value

        return translated_data
