from rest_framework import status
from rest_framework.generics import ListCreateAPIView, ListAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser

from .serializers import QuestionnaireSerializer, VoteCreateSerializer, QuestionListSerializer, QuestionPagination
from apps.shared.utils.custom_response import CustomResponse
from ..shared.permissions.mobile import IsMobileUser, IsAuthenticatedOrMobileUser
from ..shared.utils.custom_pagination import CustomPageNumberPagination
from rest_framework.generics import RetrieveAPIView
from django.db.models import Count
from .models import Questionnaire, Answer, Question


class QuestionnaireListCreateAPIView(ListCreateAPIView):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [IsAuthenticatedOrMobileUser()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED)


class QuestionnaireQuestionsListAPIView(ListAPIView):
    serializer_class = QuestionListSerializer
    permission_classes = [IsAuthenticatedOrMobileUser]
    pagination_class = QuestionPagination

    def get_queryset(self):
        questionnaire = Questionnaire.objects.get(pk=self.kwargs['questionnaire_id'])
        return Question.objects.filter(questionnaire=questionnaire).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

class VoteCreateAPIView(CreateAPIView):
    serializer_class = VoteCreateSerializer
    permission_classes = [IsAuthenticatedOrMobileUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED)
