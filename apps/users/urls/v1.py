from django.urls import path

from apps.users import views

app_name = 'users'

urlpatterns = [
    path('auth/', views.AuthAPIView.as_view(), name='auth'),
    path('verify/', views.VerifyCodeAPIView.as_view(), name='verify_code'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
]