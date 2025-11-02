from modeltranslation.translator import translator, TranslationOptions
from .models import Product, Measurement, ProductCategory


class ProductTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


translator.register(Product, ProductTranslationOptions)