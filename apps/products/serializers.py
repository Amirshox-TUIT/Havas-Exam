from django.db.models.aggregates import Avg
from rest_framework import serializers

from apps.products.models import Product, ProductRating
from apps.shared.utils.translation_serializer_mixin import TranslatableSerializerMixin
from apps.shared.mixins.translation_mixins import (
    TranslatedFieldsWriteMixin,
    TranslatedFieldsReadMixin
)


class ProductTranslationMixin:
    """Shared configuration for OnBoarding serializers"""
    translatable_fields = ['title', 'description', 'images']
    media_fields = ['images']

class ProductListSerializer(ProductTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price', 'discount_price',
                  'quantity', 'weight', 'measurement',
                  'category', 'discount', 'avg_rating', 'in_stock']

    def get_avg_rating(self, obj):
        rating = obj.ratings.aggregate(avg_rating=Avg('rating'))
        return rating['avg_rating'] if obj.ratings else 0

    def get_discount_price(self, obj):
        return obj.discount_price

    def get_in_stock(self, obj):
        return obj.in_stock()


class ProductRetrieveSerializer(ProductTranslationMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price',
                  'discount_price', 'quantity', 'weight',
                  'measurement', 'category', 'discount', 'in_stock']
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_discount_price(self, obj):
        price = obj.discount_price
        return round(price, 2)

    def get_in_stock(self, obj):
        return obj.in_stock()


class ProductRatingCreateSerializer(serializers.ModelSerializer):
    product = ProductRetrieveSerializer(read_only=True)

    class Meta:
        model = ProductRating
        fields = "__all__"

        extra_kwargs = {
            'id': {'read_only': True},
            'product': {'read_only': True},
        }

    def validate_rating(self, rating):
        if not (0 <= rating <= 5):
            raise serializers.ValidationError('Rating must be greater than 0')
        return rating

