from requests import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser

from ..serializers.histories import HistorySerializer
from ...history.models import History
from ...shared.utils.custom_pagination import CustomPageNumberPagination
from ...shared.utils.custom_response import CustomResponse


class HistoryListCreateAPIView(ListCreateAPIView):
    queryset = History.objects.all().order_by('-created_at')
    serializer_class = HistorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = CustomPageNumberPagination

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
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse.success(
            data=serializer.data,
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )


class HistoryRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return CustomResponse.success(
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(
            status_code=status.HTTP_204_NO_CONTENT,
        )