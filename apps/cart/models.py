from django.db import models

from apps.products.models import Product


class Color(models.Model):
    title = models.CharField(max_length=128)
    code = models.CharField(max_length=7)


class Measurement(models.Model):
    title = models.CharField(max_length=128)


class CartProduct(models.Model):
    products = models.OneToOneField(Product, related_name='cart', on_delete=models.CASCADE)
    measurement = models.ForeignKey(Measurement, on_delete=models.CASCADE, related_name='cart')
    quantity = models.IntegerField()
    is_completed = models.BooleanField(default=False)

class Cart(models.Model):
    title = models.CharField(max_length=128)
    color = models.ForeignKey(Color, related_name='cart', on_delete=models.CASCADE)
    cart_product = models.ForeignKey(CartProduct, related_name='cart', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'




