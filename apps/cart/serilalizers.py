from rest_framework import serializers

from apps.cart.models import Cart


class CartListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart