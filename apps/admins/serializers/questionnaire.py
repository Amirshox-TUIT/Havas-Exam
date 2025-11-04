from rest_framework import serializers
from apps.questionnaires.models import QuestionnaireStatus, Questionnaire, Question, Answer, Vote
from apps.shared.mixins.translation_mixins import TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin

class BaseMixin:
    translatable_fields = ['title']

    def validate_title_en(self, title):
        if not title.strip():
            raise serializers.ValidationError("Title must not be empty")
        return title

    def validate_title_uz(self, title):
        if not title.strip():
            raise serializers.ValidationError("Title must not be empty")
        return title

    def validate_status(self, status):
        valid_statuses = [s[0] for s in QuestionnaireStatus.choices]
        if status not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of {valid_statuses}")
        return status


class AnswerDetailSerializer(BaseMixin, TranslatedFieldsReadMixin, TranslatedFieldsWriteMixin, serializers.ModelSerializer):
    votes_count = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ('id', 'title', 'votes_count', 'percent')

    def get_votes_count(self, obj):
        return obj.votes.count()

    def get_percent(self, obj):
        total_votes = self.context.get('total_votes', 0)
        count = obj.votes.count()
        return round((count / total_votes) * 100, 2) if total_votes > 0 else 0


class QuestionDetailSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ('id', 'title', 'answers')

    def get_answers(self, obj):
        total_votes = Vote.objects.filter(answer__question=obj).count()
        serializer = AnswerDetailSerializer(obj.answers.all(), many=True, context={'total_votes': total_votes})
        return serializer.data


class QuestionnaireDetailSerializer(BaseMixin, TranslatedFieldsWriteMixin, TranslatedFieldsReadMixin, serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'status', 'questions')

    def get_questions(self, obj):
        serializer = QuestionDetailSerializer(obj.questions.all(), many=True)
        return serializer.data

