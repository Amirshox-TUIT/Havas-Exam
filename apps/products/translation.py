from modeltranslation.translator import translator, TranslationOptions
from .models import Product, Measurement, ProductCategory


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description', 'slug')


translator.register(Product, ProductTranslationOptions)