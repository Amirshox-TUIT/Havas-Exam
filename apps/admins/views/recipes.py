from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, ListCreateAPIView, get_object_or_404
from rest_framework.permissions import IsAdminUser

from apps.admins.serializers.recipes import RecipesDetailSerializer, RecipesListCreateSerializer, \
    IngredientsViewSetSerializer, PreparationStepsSerializer
from apps.products.models import Product
from apps.recipes.models import Recipe, RecipesProduct, PreparationSteps
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse


class RecipeListCreateAPIView(ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipesListCreateSerializer
    permission_classes = (IsAdminUser,)
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
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED, headers=headers)

class RecipeRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipesDetailSerializer
    permission_classes = [IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)


class IngredientsListCreateAPIView(ListCreateAPIView):
    queryset = RecipesProduct.objects.all()
    serializer_class = IngredientsViewSetSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAdminUser,)

    def get_object(self):
        return get_object_or_404(Recipe, pk=self.kwargs['pk'])

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
        recipe = self.get_object()
        product = Product.objects.get(id=serializer.validated_data.pop('product_id'))
        serializer.save(recipe=recipe, product=product)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED, headers=headers)


class IngredientsRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = IngredientsViewSetSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return RecipesProduct.objects.filter(recipe=recipe)

    def get_object(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        ingredient = get_object_or_404(RecipesProduct, id=self.kwargs['id'])
        if ingredient.recipe != recipe:
            raise Http404
        return ingredient

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)


class PreparationStepsListCreateAPIView(ListCreateAPIView):
    serializer_class = PreparationStepsSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return PreparationSteps.objects.filter(recipe=recipe)

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
        recipe = Recipe.objects.get(pk=self.kwargs['pk'])
        serializer.save(recipe=recipe)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_201_CREATED, headers=headers)


class PreparationStepsRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = PreparationStepsSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        recipe = get_object_or_404(Recipe, pk=self.kwargs['pk'])
        return PreparationSteps.objects.filter(recipe=recipe)

    def get_object(self):
        return get_object_or_404(PreparationSteps, pk=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return CustomResponse.success(status_code=status.HTTP_204_NO_CONTENT)
