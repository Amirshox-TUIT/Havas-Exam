from rest_framework import serializers

from apps.products.models import Product
from apps.recipes.models import Recipe, RecipesCategory, RecipesProduct, PreparationSteps, RecipesRating
from apps.shared.mixins.translation_mixins import (
    TranslatedFieldsReadMixin
)


class RecipeTranslationMixin:
    """Shared configuration for OnBoarding serializers"""
    translatable_fields = ['title', 'images']
    media_fields = ['images']


class InlineCategorySerializer(TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = RecipesCategory
        fields = ['title']

    translatable_fields = ['title']


class RecipesListSerializer(RecipeTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    category_title = InlineCategorySerializer(source='category')

    class Meta:
        model = Recipe
        exclude = ['is_active', 'created_at', 'updated_at', 'category']


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


class RecipesDetailSerializer(RecipeTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    category_title = InlineCategorySerializer(source='category')
    ingredients = InlineIngredientsSerializer(many=True)
    steps = InlineStepsSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ['is_active', 'created_at', 'updated_at', 'category']


class RecipeReviewCreateSerializer(serializers.ModelSerializer):
    recipe_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RecipesRating
        fields = ["rating", 'recipe_title', 'device']

        extra_kwargs = {
            'device': {'read_only': True},
        }

    def get_recipe_title(self, obj):
        return obj.recipe.title

    def validate_rating(self, rating):
        if not (0 <= rating <= 5):
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return rating




