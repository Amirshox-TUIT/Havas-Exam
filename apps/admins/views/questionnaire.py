from django.db.models import Count
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser

from apps.admins.serializers.questionnaire import QuestionnaireDetailSerializer, QuestionDetailSerializer, \
    AnswerDetailSerializer
from apps.questionnaires.models import Questionnaire, Answer, Question
from apps.shared.utils.custom_response import CustomResponse


class QuestionnaireDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireDetailSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        questionnaire = self.get_object()
        serializer = self.get_serializer(questionnaire)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return CustomResponse.success(status_code=204)


class QuestionCreateAPIView(CreateAPIView):
    serializer_class = QuestionDetailSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        questionnaire_id = self.kwargs.get("questionnaire_id")
        serializer.save(questionnaire_id=questionnaire_id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return CustomResponse.success(data=response.data, status_code=201)


class QuestionRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionDetailSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return CustomResponse.success(data=self.get_serializer(instance).data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return CustomResponse.success(data=response.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return CustomResponse.success(status_code=204)


class AnswerCreateAPIView(CreateAPIView):
    serializer_class = AnswerDetailSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        question_id = self.kwargs.get("question_id")
        serializer.save(question_id=question_id)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return CustomResponse.success(data=response.data, status_code=201)


class AnswerRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerDetailSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        return CustomResponse.success(data=self.get_serializer(self.get_object()).data)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return CustomResponse.success(data=response.data)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return CustomResponse.success(status_code=204)
