from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import RecipesRating, Recipe
from django.db.models import Avg

def recalc_avg(recipe: Recipe):
    avg = recipe.ratings.aggregate(avg=Avg('rating'))['avg'] or 0
    recipe.avg_rating = avg
    recipe.save(update_fields=['avg_rating'])


@receiver(post_save, sender=RecipesRating)
def update_avg_on_save(sender, instance, **kwargs):
    recalc_avg(instance.recipe)


@receiver(post_delete, sender=RecipesRating)
def update_avg_on_delete(sender, instance, **kwargs):
    recalc_avg(instance.recipe)