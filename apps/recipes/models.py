from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

from apps.products.models import Product, Measurement
from apps.users.models.device import Device

User = get_user_model()

class RecipesCategory(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'
        verbose_name = 'Category'


class Recipe(models.Model):
    title = models.CharField(max_length=128)
    category = models.ForeignKey(RecipesCategory, on_delete=models.CASCADE, related_name='recipes')
    calories = models.IntegerField()
    cooking_time = models.IntegerField()
    media_files = GenericRelation(
        'shared.Media',
        related_query_name='recipes'
    )
    avg_rating = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Recipes'
        verbose_name = 'Recipe'


class RecipesProduct(models.Model):
    product = models.ForeignKey(Product, related_name='recipes', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    measurement = models.CharField(max_length=16, choices=Measurement.choices, default=Measurement.GR)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')

    def __str__(self):
        return self.product.title

    class Meta:
        ordering = ['quantity']
        verbose_name_plural = 'Products'
        verbose_name = 'Product'


class PreparationSteps(models.Model):
    description = models.TextField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='steps')

    def __str__(self):
        return f"{self.recipe.title}-{self.description[:10]}"

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Preparation Steps'
        verbose_name = 'Preparation Step'


class RecipesRating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='recipes_ratings')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])

    def __str__(self):
        return f"{self.recipe.title} - {self.rating}"

    class Meta:
        ordering = ['rating']
        verbose_name_plural = 'Ratings'
        verbose_name = 'Rating'