from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.carts.models import Cart, CartProduct
from apps.carts.serilalizers import CartListCreateSerializer, CartDetailSerializer, CartProductCreateSerializer
from apps.shared.exceptions.custom_exceptions import CustomException
from apps.shared.permissions.mobile import IsMobileUser
from apps.shared.utils.custom_pagination import CustomPageNumberPagination
from apps.shared.utils.custom_response import CustomResponse
from apps.users.models.device import Device


class CartListCreateAPIView(ListCreateAPIView):
    serializer_class = CartListCreateSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated | IsMobileUser]

    def get_queryset(self):
        queryset = Cart.objects.filter(device__device_token=self.request.headers.get('Token', '1'))
        return queryset

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
                request=request,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        device = Device.objects.get(device_token=self.request.headers.get('Token', '1'))
        if not device:
            device = self.request.user.devices.first()

        serializer.save(device=device)
        return CustomResponse.success(
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CartDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartDetailSerializer
    permission_classes = [IsAuthenticated | IsMobileUser]
    queryset = Cart.objects.all()

    def get_object(self):
        cart = Cart.objects.filter(id=self.kwargs['pk']).first()
        if not cart:
            raise CustomException(message_key="NOT_FOUND")
        device = Device.objects.get(device_token=self.request.headers.get('Token', '1'))

        if not device and cart.device.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        if cart.device != device:
            raise CustomException(message_key="PERMISSION_DENIED")

        return cart

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


class CartProductCreateAPIView(CreateAPIView):
    serializer_class = CartProductCreateSerializer
    permission_classes = [IsAuthenticated | IsMobileUser]
    queryset = Cart.objects.all()

    def get_object(self):
        cart = Cart.objects.filter(id=self.kwargs['pk']).first()
        if not cart:
            raise CustomException(message_key="NOT_FOUND")
        device = Device.objects.get(device_token=self.request.headers.get('Token', '1'))

        if not device and cart.device.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        if cart.device != device:
            raise CustomException(message_key="PERMISSION_DENIED")

        return cart

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse.error(
                message_key="VALIDATION_ERROR",
                request=request,
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        cart = self.get_object()
        serializer.save(cart=cart)
        return CustomResponse.success(
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )


class CartProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartProductCreateSerializer
    permission_classes = [IsAuthenticated | IsMobileUser]
    queryset = Cart.objects.all()

    def get_object(self):
        product = CartProduct.objects.filter(id=self.kwargs['id']).first()
        if not product:
            raise CustomException(message_key="NOT_FOUND")

        cart = product.cart
        device = Device.objects.get(device_token=self.request.headers.get('Token', '1'))
        if not device and cart.device.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        if cart.device != device:
            raise CustomException(message_key="PERMISSION_DENIED")

        return product

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


class CartProductCompletedAPIView(APIView):
    permission_classes = [IsAuthenticated | IsMobileUser]
    queryset = Cart.objects.all()

    def get_object(self):
        product = CartProduct.objects.filter(id=self.kwargs['id']).first()
        if not product:
            raise CustomException(message_key="NOT_FOUND")
        cart = product.cart
        device = Device.objects.get(device_token=self.request.headers.get('Token', '1'))
        if not device and cart.device.user != self.request.user:
            raise CustomException(message_key="PERMISSION_DENIED")
        if cart.device != device:
            raise CustomException(message_key="PERMISSION_DENIED")
        return product

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        product.is_completed = not product.is_completed
        product.save()
        return CustomResponse.success(
            data={"is_completed": product.is_completed},
            status_code=status.HTTP_200_OK
        )




