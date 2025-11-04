from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from .models import Questionnaire, QuestionnaireStatus, Vote
from ..shared.mixins.translation_mixins import TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin
from .models import Questionnaire, Question, Answer


class BaseMixin:
    translatable_fields = ['title']

    def validation_title_en(self, title):
        if len(title.strip()) <= 0:
            raise serializers.ValidationError('Title must not be empty')
        return title

    def validation_title_uz(self, title):
        if len(title.strip()) <= 0:
            raise serializers.ValidationError('Title must not be empty')
        return title

    def validate_status(self, status):
        statuses = [status[0] for status in QuestionnaireStatus.choices]
        if status not in statuses:
            raise serializers.ValidationError('Status must be one of {}'.format(statuses))
        return status


class QuestionnaireSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    questions_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Questionnaire
        fields = "__all__"
        read_only_fields = ['id', 'questions_count', 'created_at']


class QuestionPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'


class AnswerOptionSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'title']


class QuestionListSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    answers = AnswerOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'answers']


class VoteCreateSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.Serializer):
    answer_id = serializers.IntegerField()

    def validate_answer_id(self, value):
        try:
            answer = Answer.objects.get(id=value)
        except Answer.DoesNotExist:
            raise serializers.ValidationError("Answer not found")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        answer = Answer.objects.get(id=validated_data['answer_id'])

        Vote.objects.filter(
            user=user,
            answer__question=answer.question
        ).delete()

        return Vote.objects.create(answer=answer, user=user)


