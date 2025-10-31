from django.db.models.aggregates import Avg
from rest_framework import serializers

from apps.products.models import Product, ProductRating
from apps.shared.utils.translation_serializer_mixin import TranslatableSerializerMixin


class ProductListSerializer(TranslatableSerializerMixin):
    avg_rating = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'price',
                  'discount_price', 'quantity', 'weight',
                  'measurement', 'category', 'discount',
                  'image', 'slug']

    def get_avg_rating(self, obj):
        rating = obj.ratings.aggregate(avg_rating=Avg('rating'))
        return rating['avg_rating'] if obj.ratings else 0

    def get_discount_price(self, obj):
        return obj.discount_price()

    def get_in_stock(self, obj):
        return obj.in_stock()

    # def validate_title_(self, title):
    #     if len(title.strip()) < 5:
    #         raise serializers.ValidationError('Title must be at least 5 characters')
    #     return title
    #
    # def validate_description(self, description):
    #     if len(description.strip()) < 30:
    #         raise serializers.ValidationError('Description must be at least 30 characters')
    #     return description
    #
    # def validate_price(self, price):
    #     if price <= 0:
    #         raise serializers.ValidationError('Price must be greater than 0')
    #     return price
    #
    # def validate_discount(self, discount):
    #     if discount < 0:
    #         raise serializers.ValidationError('Discount must be greater than 0')
    #     return discount
    #
    # def validate_quantity(self, quantity):
    #     if quantity < 0:
    #         raise serializers.ValidationError('Quantity must be greater than 0')
    #
    #     return quantity
    #
    # def validate_weight(self, weight):
    #     if weight and weight < 0:
    #         raise serializers.ValidationError('Weight must be greater than 0')
    #     return weight


class ProductRetrieveSerializer(TranslatableSerializerMixin):
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price',
                  'discount_price', 'quantity', 'weight',
                  'measurement', 'category', 'discount',
                  'image', 'slug']
        extra_kwargs = {
            'id': {'read_only': True},
            'slug': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_discount_price(self, obj):
        price = obj.discount_price()
        return round(price, 2)

    def get_in_stock(self, obj):
        return obj.in_stock()

    # def validate_title(self, title):
    #     if len(title.strip()) < 5:
    #         raise serializers.ValidationError('Title must be at least 5 characters')
    #     return title
    #
    # def validate_description(self, description):
    #     if len(description.strip()) < 30:
    #         raise serializers.ValidationError('Description must be at least 30 characters')
    #     return description
    #
    # def validate_price(self, price):
    #     if price <= 0:
    #         raise serializers.ValidationError('Price must be greater than 0')
    #     return price
    #
    # def validate_discount(self, discount):
    #     if discount < 0:
    #         raise serializers.ValidationError('Discount must be greater than 0')
    #     return discount
    #
    # def validate_quantity(self, quantity):
    #     if quantity < 0:
    #         raise serializers.ValidationError('Quantity must be greater than 0')
    #     return quantity
    #
    # def validate_weight(self, weight):
    #     if weight and weight < 0:
    #         raise serializers.ValidationError('Weight must be greater than 0')
    #     return weight


class ProductRatingCreateSerializer(serializers.ModelSerializer):
    product = ProductRetrieveSerializer(read_only=True)

    class Meta:
        model = ProductRating
        fields = "__all__"

        extra_kwargs = {
            'id': {'read_only': True},
            'product': {'read_only': True},
            'user': {'required': False},
        }

    def validate_rating(self, rating):
        if not (0 <= rating <= 5):
            raise serializers.ValidationError('Rating must be greater than 0')
        return rating

