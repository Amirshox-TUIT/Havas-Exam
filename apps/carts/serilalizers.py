from rest_framework import serializers

from apps.carts.models import Cart, Color, CartProduct
from apps.products.models import Product, Measurement


class CartListCreateSerializer(serializers.ModelSerializer):
    completed_products = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), write_only=True)
    color_code = serializers.SerializerMethodField(read_only=True)
    device_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cart
        exclude = ('updated_at',)
        extra_kwargs = {
            'id': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }

    def get_device_id(self, obj):
        return obj.device.id

    def get_completed_products(self, obj):
        return obj.completed_products if obj.completed_products else 0

    def get_color_code(self, obj):
        return obj.color.code

    def get_total_products(self, obj):
        return obj.total_products

    def validate_title(self, title):
        if not (1 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 1 and 128 characters long')
        return title


class InlineCartProductsSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField()

    class Meta:
        model = CartProduct
        fields = ['product_title', 'quantity', 'measurement', 'is_completed']

    def get_product_title(self, obj):
        return obj.product.title


class CartDetailSerializer(serializers.ModelSerializer):
    color_code = serializers.SerializerMethodField(read_only=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), write_only=True)
    products = InlineCartProductsSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', "title", 'color_code', 'color', 'products',]

    def get_color_code(self, obj):
        return obj.color.code

    def validate_title(self, title):
        if not (1 <= len(title.strip()) <= 128):
            raise serializers.ValidationError('Title must be between 1 and 128 characters long')
        return title


class CartProductCreateSerializer(serializers.ModelSerializer):
    product_title = serializers.SerializerMethodField(read_only=True)
    product_images = serializers.SerializerMethodField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = CartProduct
        fields = ['id', 'product_images', 'product_title', 'quantity', 'measurement', 'product']

    def get_product_images(self, obj):
        return [m.file.url for m in obj.product.media_files.all()]

    def get_product_title(self, obj):
        return obj.product.title

    def validate_quantity(self, quantity):
        if quantity < 1:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return quantity

    def validate_measurement(self, measurement):
        valid_values = [m[0] for m in Measurement.choices]
        if measurement not in valid_values:
            raise serializers.ValidationError('measurement must be in Measurements')
        return measurement
