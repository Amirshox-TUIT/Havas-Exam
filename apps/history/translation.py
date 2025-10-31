from modeltranslation.translator import translator, TranslationOptions
from .models import History


class HistoryTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description', 'long_description', 'button_text')


translator.register(History, HistoryTranslationOptions)