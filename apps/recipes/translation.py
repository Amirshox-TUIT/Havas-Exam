from modeltranslation.translator import register, TranslationOptions
from .models import RecipesCategory, Recipe, PreparationSteps

@register(RecipesCategory)
class RecipesCategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Recipe)
class RecipeTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(PreparationSteps)
class PreparationStepsTranslationOptions(TranslationOptions):
    fields = ('description',)
