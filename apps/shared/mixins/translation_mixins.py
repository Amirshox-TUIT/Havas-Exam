from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class TranslatedFieldsWriteMixin:
    """
    Mixin for CREATE/UPDATE serializers
    Handles text translations and media uploads
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.languages = settings.LANGUAGES

        translatable_fields = getattr(self, 'translatable_fields', [])
        media_fields = getattr(self, 'media_fields', [])

        # Create language-specific fields for translatable fields
        for field_name in translatable_fields:
            is_media = field_name in media_fields

            # Make base field optional if exists
            if field_name in self.fields:
                self.fields[field_name].required = False

            # Create language fields
            for lang_code, lang_name in self.languages:
                field_key = f"{field_name}_{lang_code.lower()}"

                if is_media:
                    # Media field
                    is_list = field_name.endswith('s')
                    if is_list:
                        self.fields[field_key] = serializers.ListField(
                            child=serializers.FileField(),
                            required=False,
                            allow_empty=True,
                            help_text=f"{lang_name} files"
                        )
                    else:
                        self.fields[field_key] = serializers.FileField(
                            required=False,
                            allow_null=True,
                            help_text=f"{lang_name} file"
                        )
                elif field_name in self.fields:
                    # Text field
                    original = self.fields[field_name]
                    self.fields[field_key] = original.__class__(
                        required=True,
                        allow_blank=True,
                        allow_null=True,
                        help_text=f"{lang_name} translation",
                        max_length=getattr(original, 'max_length', None)
                    )

        # Create non-translatable media fields (shared)
        for field_name in media_fields:
            if field_name not in translatable_fields:
                is_list = field_name.endswith('s')
                if is_list:
                    self.fields[field_name] = serializers.ListField(
                        child=serializers.FileField(),
                        required=False,
                        allow_empty=True,
                        help_text="Media files"
                    )
                else:
                    self.fields[field_name] = serializers.FileField(
                        required=False,
                        allow_null=True,
                        help_text="Media file"
                    )

    def create(self, validated_data):
        media_data = self._extract_media_data(validated_data)
        for field in self.fields:
            print(field)
        instance = super().create(validated_data)
        self._save_media_files(instance, media_data)
        return instance

    def update(self, instance, validated_data):
        media_data = self._extract_media_data(validated_data)
        instance = super().update(instance, validated_data)
        self._save_media_files(instance, media_data)
        return instance

    def _extract_media_data(self, validated_data):
        """Extract media files from validated_data"""

        media_fields = getattr(self, 'media_fields', [])
        translatable_fields = getattr(self, 'translatable_fields', [])
        media_data = {}

        for field_name in media_fields:
            is_translatable = field_name in translatable_fields

            if is_translatable:
                # Get language-specific files
                for lang_code, _ in self.languages:
                    key = f"{field_name}_{lang_code.lower()}"
                    if key in validated_data:
                        media_data[key] = validated_data.pop(key)
            else:
                # Get shared files
                if field_name in validated_data:
                    media_data[field_name] = validated_data.pop(field_name)

        return media_data

    def _save_media_files(self, instance, media_data):
        """Save media files to Media model"""
        from apps.shared.models import Media

        if not media_data:
            return

        content_type = ContentType.objects.get_for_model(instance)
        request = self.context.get('request')
        user = request.user if request and hasattr(request, 'user') else None

        for field_name, files in media_data.items():
            if not files:
                continue

            # Detect language
            language = None
            base_field = field_name
            for lang_code, _ in self.languages:
                suffix = f"_{lang_code.lower()}"
                if field_name.endswith(suffix):
                    language = lang_code
                    base_field = field_name.replace(suffix, '')
                    break

            # Detect media type
            if 'image' in base_field.lower():
                media_type = 'image'
            elif 'video' in base_field.lower():
                media_type = 'video'
            elif 'audio' in base_field.lower():
                media_type = 'audio'
            elif 'document' in base_field.lower() or 'file' in base_field.lower():
                media_type = 'document'
            else:
                media_type = 'other'

            # Save files
            file_list = files if isinstance(files, list) else [files]
            for file_obj in file_list:
                if file_obj:
                    Media.objects.create(
                        content_type=content_type,
                        object_id=instance.pk,
                        file=file_obj,
                        media_type=media_type,
                        original_filename=file_obj.name,
                        uploaded_by=user,
                        language=language,
                        is_public=True
                    )


class TranslatedFieldsReadMixin:
    """
    Mixin for GET/LIST serializers
    Returns content in language from request.lang
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)

        translatable_fields = getattr(self, 'translatable_fields', [])
        media_fields = getattr(self, 'media_fields', [])

        request = self.context.get('request')
        lang = self._get_language(request)

        # Handle translatable fields
        for field_name in translatable_fields:
            if field_name in media_fields:
                # Media field
                data[field_name] = self._get_media(instance, field_name, lang)
            else:
                # Text field
                field_key = f"{field_name}_{lang}"
                if hasattr(instance, field_key):
                    value = getattr(instance, field_key, '')
                    data[field_name] = value if value else ''

            # Remove language fields
            for lc, _ in settings.LANGUAGES:
                data.pop(f"{field_name}_{lc.lower()}", None)

        # Handle non-translatable media
        for field_name in media_fields:
            if field_name not in translatable_fields:
                data[field_name] = self._get_media(instance, field_name, None)

        return data

    def _get_language(self, request):
        return 'en'

    def _get_media(self, instance, field_name, language):
        is_list = field_name.endswith('s')

        # Detect media type from base field name (remove 's' for plural)
        base_name = field_name.rstrip('s') if is_list else field_name

        if 'image' in base_name.lower():
            media_type = 'image'
        elif 'video' in base_name.lower():
            media_type = 'video'
        elif 'audio' in base_name.lower():
            media_type = 'audio'
        elif 'document' in base_name.lower() or 'file' in base_name.lower():
            media_type = 'document'
        else:
            media_type = 'other'

        if language:
            # Language-specific media
            lang_map = {l[0].lower(): l[0] for l in settings.LANGUAGES}
            db_lang = lang_map.get(language)
            qs = instance.media_files.filter(media_type=media_type, language=db_lang)
        else:
            # Shared media (no language)
            qs = instance.media_files.filter(media_type=media_type, language__isnull=True)

        # Return list or single object
        if is_list:
            return [{
                'id': str(m.id),
                'url': m.file.url if m.file else None,
                'filename': m.original_filename,
                'size': m.file_size,
                'type': m.media_type,
                'language': m.language
            } for m in qs]
        else:
            first = qs.first()
            if first:
                return {
                    'id': str(first.id),
                    'url': first.file.url if first.file else None,
                    'filename': first.original_filename,
                    'size': first.file_size,
                    'type': first.media_type,
                    'language': first.language
                }
            return None
