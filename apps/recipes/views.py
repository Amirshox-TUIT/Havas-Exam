from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView

from apps.carts.models import Cart, CartProduct
from apps.products.models import Product
from apps.recipes.models import Recipe, RecipesProduct
from apps.recipes.serializers import RecipesListSerializer, RecipesDetailSerializer, RecipeReviewCreateSerializer
from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.permissions.mobile import IsMobileUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse
from apps.users.models.device import Device


class RecipesListAPI(ListAPIView):
    pagination_class = CustomPageNumberPagination
    serializer_class = RecipesListSerializer
    permission_classes = [IsMobileUser | IsAuthenticated]

    def get_queryset(self):
        recipes = Recipe.objects.filter(is_active=True)
        category_id = self.request.GET.get('category_id')
        rating = self.request.GET.get('rating')
        min_calories = self.request.GET.get('min_calories')
        max_calories = self.request.GET.get('max_calories')
        min_cooking_time = self.request.GET.get('min_cooking_time')
        max_cooking_time = self.request.GET.get('max_cooking_time')
        order_by = self.request.GET.get('order_by')
        if category_id:
            recipes = recipes.filter(category_id=category_id)
        if rating:
            recipes = recipes.filter(avg_rating=int(rating))
        if min_calories:
            recipes = recipes.filter(calories__gte=int(min_calories))
        if max_calories:
            recipes = recipes.filter(calories__lte=int(max_calories))
        if min_cooking_time:
            recipes = recipes.filter(cooking_time__gte=int(min_cooking_time))
        if max_cooking_time:
            recipes = recipes.filter(cooking_time__lte=int(max_cooking_time))
        if order_by:
            recipes = recipes.order_by(order_by)
        return recipes


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class RecipeDetailAPI(RetrieveAPIView):
    serializer_class = RecipesDetailSerializer
    permission_classes = [IsMobileUser | IsAuthenticated]
    queryset = Recipe.objects.filter(is_active=True)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return CustomResponse.success(data=serializer.data, status_code=status.HTTP_200_OK)


class IngredientsToProductBulkCreateAPIView(APIView):
    permission_classes = [IsMobileUser | IsAuthenticated]

    def post(self, request, *args, **kwargs):
        ingredient_ids = request.data.get('ingredients')
        carts_ids = request.data.get('carts')
        ingredients = RecipesProduct.objects.filter(id__in=ingredient_ids)
        carts = Cart.objects.filter(id__in=carts_ids)
        if not carts or not ingredients:
            return CustomResponse.error(
                message_key="NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        token = request.headers.get('Token')
        auth_user = request.user if request.user.is_authenticated else None

        device = None
        if token:
            try:
                device = Device.objects.get(device_token=token)
            except Device.DoesNotExist:
                raise CustomException(message_key="USER_NOT_FOUND")

        for cart in carts:
            if auth_user:
                if cart.device.user != auth_user:
                    raise CustomException(message_key="PERMISSION_DENIED")

            if device:
                if cart.device != device:
                    raise CustomException(message_key="PERMISSION_DENIED")

        cart_products = []
        for cart in carts:
            for ingredient in ingredients:
                cart_products.append(
                    CartProduct(
                        product=ingredient.product,
                        measurement=ingredient.measurement,
                        quantity=ingredient.quantity,
                        cart=cart,
                    )
                )

        CartProduct.objects.bulk_create(cart_products)

        return CustomResponse.success(status_code=status.HTTP_201_CREATED)


class RecipeReviewCreateAPIView(CreateAPIView):
    permission_classes = [IsMobileUser | IsAuthenticated]
    serializer_class = RecipeReviewCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(message_key="VALIDATION_ERROR", errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        device = request.user.device if request.user.is_authenticated else Device.objects.get(device_token=request.headers.get('Token'))
        recipe = get_object_or_404(Recipe, id=self.kwargs['pk'])
        serializer.save(recipe=recipe, device=device)
        headers = self.get_success_headers(serializer.data)
        return CustomResponse.success(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)
