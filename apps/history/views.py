from django.utils import translation
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from apps.history.models import History
from apps.history.serializers import HistoryListSerializer, HistoryRetrieveSerializer
from apps.shared.permissions.mobile import IsMobileUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class HistoryListAPIView(ListAPIView):
    queryset = History.objects.filter(is_active=True)
    serializer_class = HistoryListSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsMobileUser | IsAuthenticated | IsAdminUser]

    def list(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        translation.activate(lang)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class HistoryRetrieveAPIView(RetrieveAPIView):
    queryset = History.objects.filter(is_active=True)
    serializer_class = HistoryRetrieveSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsMobileUser | IsAuthenticated | IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        lang = request.query_params.get('lang', 'en')
        translation.activate(lang)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)
