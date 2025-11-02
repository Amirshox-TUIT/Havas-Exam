from django.db import models

from apps.products.models import Product, Measurement
from apps.users.models.device import Device

class Color(models.Model):
    title = models.CharField(max_length=128)
    code = models.CharField(max_length=7)


class Cart(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='carts', default=1)
    title = models.CharField(max_length=128)
    color = models.ForeignKey(Color, related_name='carts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def completed_products(self):
        return self.products.filter(is_completed=True).count()

    @property
    def total_products(self):
        return self.products.all().count()

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'


class CartProduct(models.Model):
    product = models.ForeignKey(Product, related_name='carts', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    measurement = models.CharField(max_length=16, choices=Measurement.choices, default=Measurement.GR)
    is_completed = models.BooleanField(default=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='products')


