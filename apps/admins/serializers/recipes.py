from rest_framework import serializers

from apps.products.models import Product, Measurement
from apps.recipes.models import Recipe, RecipesProduct, PreparationSteps, RecipesCategory
from apps.shared.mixins.translation_mixins import TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin


class RecipeTranslationMixin:
    """Shared configuration for OnBoarding serializers"""
    translatable_fields = ['title', 'images']
    media_fields = ['images']


class InlineCategorySerializer(TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = RecipesCategory
        fields = ['title']

    translatable_fields = ['title']


class RecipesListCreateSerializer(RecipeTranslationMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    category_title = InlineCategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=RecipesCategory.objects.all(), write_only=True)

    class Meta:
        model = Recipe
        exclude = ['created_at', 'updated_at']
        extra_kwargs = {
            'avg_rating': {'read_only': True},
        }

    def validate_title_en(self, title):
        if not (5 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 5 and 128 characters long')
        return title

    def validate_title_uz(self, title):
        if not (5 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 5 and 128 characters long')
        return title

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise serializers.ValidationError('Cooking time must be greater than 0')
        return cooking_time

    def validate_calories(self, calories):
        if calories <= 0:
            raise serializers.ValidationError('Calories must be greater than 0')
        return calories

    def validate_is_active(self, is_active):
        if not isinstance(is_active, bool):
            raise serializers.ValidationError('is_active must be of type bool')
        return is_active



class InlineProductSerializer(TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['title']

    translatable_fields = ['title', 'images']
    media_fields = ['image']


class InlineIngredientsSerializer(serializers.ModelSerializer):
    product = InlineProductSerializer()

    class Meta:
        model = RecipesProduct
        fields = ['product', 'quantity', 'measurement']


class InlineStepsSerializer(TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = PreparationSteps
        fields = ['description']

    translatable_fields = ['description']


class RecipesDetailSerializer(RecipeTranslationMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    category_title = InlineCategorySerializer(source='category', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=RecipesCategory.objects.all(), write_only=True)

    class Meta:
        model = Recipe
        exclude = ['created_at', 'updated_at']
        extra_kwargs = {
            'avg_rating': {'read_only': True},
        }

    def validate_title_en(self, title):
        if not (5 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 5 and 128 characters long')
        return title

    def validate_title_uz(self, title):
        if not (5 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 5 and 128 characters long')
        return title

    def validate_cooking_time(self, cooking_time):
        if cooking_time <= 0:
            raise serializers.ValidationError('Cooking time must be greater than 0')
        return cooking_time

    def validate_calories(self, calories):
        if calories <= 0:
            raise serializers.ValidationError('Calories must be greater than 0')
        return calories

    def validate_is_active(self, is_active):
        if not isinstance(is_active, bool):
            raise serializers.ValidationError('is_active must be of type bool')
        return is_active


class IngredientsViewSetSerializer(serializers.ModelSerializer):
    product = InlineProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipesProduct
        exclude = ['id', ]
        extra_kwargs = {
            'recipe':{'required':False}
        }

    def validate_product_id(self, product_id):
        if not Product.objects.filter(id=product_id).exists():
            raise serializers.ValidationError('product_id must be an existing product')
        return product_id

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return quantity

    def validate_measurement(self, measurement):
        measurements = [measurement[0] for measurement in Measurement.choices]
        if measurement not in measurements:
            raise serializers.ValidationError('Measurement must be one of {}'.format(', '.join(measurements)))
        return measurement


class PreparationStepsSerializer(TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin, serializers.ModelSerializer):
    class Meta:
        model = PreparationSteps
        exclude = ['id','recipe']

    translatable_fields = ['description']

    def validate_description_en(self, description):
        if len(description.strip()) < 2:
            raise serializers.ValidationError('Description must be at least 2 characters long')
        return description

    def validate_description_uz(self, description):
        if len(description.strip()) < 2:
            raise serializers.ValidationError('Description must be at least 2 characters long')
        return description

