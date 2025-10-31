from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.text import slugify

User = get_user_model()

class Measurement(models.TextChoices):
    GR = ('gr', 'Gram')
    KG = ('kg', 'Kilogram')
    PC = ('pc', 'Piece')
    L = ('l', 'Litre')
    ML = ('ml', 'Milliliter')


class ProductCategory(models.TextChoices):
    BF = ('bf', 'Breakfast')
    LU = ('lu', 'Lunch')
    DN = ('dn', 'Dinner')
    ALL = ('all', 'All')


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
    weight = models.PositiveIntegerField(null=True, blank=True)
    measurement = models.CharField(
        max_length=12,
        choices=Measurement.choices,
        default=Measurement.GR
    )
    category = models.CharField(
        max_length=12,
        choices=ProductCategory.choices,
        default=ProductCategory.ALL
    )
    discount = models.PositiveSmallIntegerField(default=0)
    image = models.ImageField(null=True, blank=True, upload_to='products/')
    slug = models.SlugField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def in_stock(self):
        return self.quantity > 0

    def save(self, *args, **kwargs):
        new_slug = slugify(self.title)
        if not self.slug or new_slug != self.slug:
            

            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def discount_price(self):
        discount_multiplier = Decimal(100 - self.discount) / Decimal(100)
        return (self.price * discount_multiplier).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Products"
        verbose_name = "Product"


class ProductRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        name = self.user.first_name if self.user.first_name else 'unknown'
        return f"{name} - {self.product.title}-{self.rating}"

    class Meta:
        verbose_name_plural = "Ratings"
        verbose_name = "Rating"




