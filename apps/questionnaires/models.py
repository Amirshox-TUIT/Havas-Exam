from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()

class QuestionnaireStatus(models.TextChoices):
    DRAFT = ('draft', 'DRAFT')
    PUBLISHED = ('published', 'PUBLISHED')
    EXPIRED = ('expired', 'EXPIRED')


class Questionnaire(models.Model):
    title = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=QuestionnaireStatus.choices, max_length=32, default=QuestionnaireStatus.PUBLISHED)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Questionnaires"
        verbose_name = "Questionnaire"

    @property
    def questions_count(self):
        return self.questions.count()


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='questions')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Questions"
        verbose_name = "Question"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.question.title

    class Meta:
        verbose_name_plural = "Answers"
        verbose_name = "Answer"


class Vote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return self.answer.title

    class Meta:
        verbose_name_plural = "Votes"
        verbose_name = "Vote"

