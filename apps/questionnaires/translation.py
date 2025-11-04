from modeltranslation.translator import register, TranslationOptions
from .models import Questionnaire, Question, Answer

@register(Questionnaire)
class QuestionnaireTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(Question)
class QuestionTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(Answer)
class AnswerTranslationOptions(TranslationOptions):
    fields = ('title',)
