from django.db.models.aggregates import Avg
from rest_framework import serializers

from apps.products.models import Product, ProductRating
from apps.users.serializers import ProfileRetrieveUpdateSerializer


class ProductListCreateSerializer(serializers.ModelSerializer):
    avg_rating = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_avg_rating(self, obj):
        rating = obj.ratings.aggregate(avg_rating=Avg('rating'))
        return rating['avg_rating'] if obj.ratings else 0

    def get_discount_price(self, obj):
        return obj.discount_price()

    def get_in_stock(self, obj):
        return obj.in_stock()

    def validate_title(self, title):
        if len(title.strip()) < 5:
            raise serializers.ValidationError('Title must be at least 5 characters')
        return title

    def validate_description(self, description):
        if len(description.strip()) < 30:
            raise serializers.ValidationError('Description must be at least 30 characters')
        return description

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError('Price must be greater than 0')
        return price

    def validate_discount(self, discount):
        if discount < 0:
            raise serializers.ValidationError('Discount must be greater than 0')
        return discount

    def validate_quantity(self, quantity):
        if quantity < 0:
            raise serializers.ValidationError('Quantity must be greater than 0')

        return quantity

    def validate_weight(self, weight):
        if weight and weight < 0:
            raise serializers.ValidationError('Weight must be greater than 0')
        return weight


class ProductRetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    discount_price = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
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

    def validate_title(self, title):
        if len(title.strip()) < 5:
            raise serializers.ValidationError('Title must be at least 5 characters')
        return title

    def validate_description(self, description):
        if len(description.strip()) < 30:
            raise serializers.ValidationError('Description must be at least 30 characters')
        return description

    def validate_price(self, price):
        if price <= 0:
            raise serializers.ValidationError('Price must be greater than 0')
        return price

    def validate_discount(self, discount):
        if discount < 0:
            raise serializers.ValidationError('Discount must be greater than 0')
        return discount

    def validate_quantity(self, quantity):
        if quantity < 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return quantity

    def validate_weight(self, weight):
        if weight and weight < 0:
            raise serializers.ValidationError('Weight must be greater than 0')
        return weight


class ProductRatingCreateSerializer(serializers.ModelSerializer):
    product = ProductRetrieveUpdateDestroySerializer(read_only=True)

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

