from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from apps.products.models import Product, ProductRating
from apps.products.serializers import ProductListCreateSerializer, ProductRetrieveUpdateDestroySerializer, \
    ProductRatingCreateSerializer
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductListCreateSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class ProductRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductRetrieveUpdateDestroySerializer
    pagination_class = CustomPageNumberPagination



    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs['pk'], is_available=True)

    def delete(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_available = False
        product.save()
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class ProductRatingCreateAPIView(CreateAPIView):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductRatingCreateSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(Product, pk=self.kwargs['pk'], is_available=True)

    def create(self, request, *args, **kwargs):
        user = self.request.user
        product = self.get_object()
        if ProductRating.objects.filter(user=user, product=product).exists():
            return Response({'message': 'Product already rated.'}, status=status.HTTP_409_CONFLICT)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, product=product)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_201_CREATED)




