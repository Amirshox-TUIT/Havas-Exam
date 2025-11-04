from rest_framework import status
from rest_framework.generics import get_object_or_404, CreateAPIView, \
    ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.products.models import Product, ProductRating
from apps.products.serializers import ProductListSerializer, ProductRetrieveSerializer, \
    ProductRatingCreateSerializer
from apps.shared.permissions.mobile import IsMobileUser, IsAuthenticatedOrMobileUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductListSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsMobileUser | IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductRetrieveSerializer
    pagination_class = CustomPageNumberPagination
    # permission_classes = [IsMobileUser | IsAuthenticated]
    permission_classes = [AllowAny]

    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs['pk'], is_available=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class ProductRatingCreateAPIView(CreateAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductRatingCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs['pk'], is_available=True)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        product = self.get_object()
        if ProductRating.objects.filter(user=user, product=product).exists():
            return CustomResponse.error(message_key='VALIDATION_ERROR', data={'message': 'Product already rated.'}, status_code=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, product=product)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_201_CREATED)




