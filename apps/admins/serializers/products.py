from decimal import Decimal
from rest_framework import serializers
from apps.products.models import Product
from apps.shared.mixins.translation_mixins import TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin


class ProductTranslationMixin:
    translatable_fields = ['title', 'description', 'images']
    media_fields = ['images']


class ProductAdminSerializer(ProductTranslationMixin, TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin,
                             serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    discount_price = serializers.SerializerMethodField(read_only=True)
    in_stock = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'weight': {'required': False, 'allow_null': True},
            'discount': {'required': False},
            'is_available': {'required': False},
        }

    def get_discount_price(self, obj):
        return float(obj.discount_price)

    def get_in_stock(self, obj):
        return obj.in_stock()

    def validate_title(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                'Title must be at least 5 characters long'
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                'Title cannot exceed 100 characters'
            )
        return value.strip()

    def validate_description(self, value):
        if len(value.strip()) < 30:
            raise serializers.ValidationError(
                'Description must be at least 30 characters long'
            )
        return value.strip()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Price must be greater than 0'
            )
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Quantity cannot be negative'
            )
        return value

    def validate_weight(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                'Weight must be greater than 0'
            )
        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Discount cannot be negative'
            )
        if value > 100:
            raise serializers.ValidationError(
                'Discount cannot exceed 100%'
            )
        return value

    def validate(self, attrs):
        price = attrs.get('price', self.instance.price if self.instance else None)
        discount = attrs.get('discount', self.instance.discount if self.instance else 0)

        if price and discount:
            discount_multiplier = Decimal(100 - discount) / Decimal(100)
            discount_price = price * discount_multiplier

            if discount > 0 and discount_price >= price:
                raise serializers.ValidationError({
                    'discount': 'Discount price must be less than original price'
                })

        weight = attrs.get('weight')
        measurement = attrs.get('measurement', self.instance.measurement if self.instance else None)

        if weight and not measurement:
            raise serializers.ValidationError({
                'measurement': 'Measurement is required when weight is provided'
            })

        return attrs
