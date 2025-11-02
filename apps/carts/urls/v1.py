from django.urls import path

from apps.carts import views

app_name = 'carts'

urlpatterns = [
    path('', views.CartListCreateAPIView.as_view(), name='list'),
    path('<int:pk>/', views.CartDetailAPIView.as_view(), name='detail'),
    path('<int:pk>/products/', views.CartProductCreateAPIView.as_view(), name='cart_product'),
    path('<int:pk>/products/<int:id>/', views.CartProductDetailAPIView.as_view(), name='cart_product_detail'),
    path('<int:pk>/products/<int:id>/completed/', views.CartProductCompletedAPIView.as_view(), name='cart_product_completed'),
]