from django.urls import path

from apps.users import views
from apps.users.views import DeviceRegisterCreateAPIView, DeviceListApiView

app_name = 'users'

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('verify/', views.VerifyCodeAPIView.as_view(), name='verify_code'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('forgot-password/', views.ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path('profile/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('set-password/', views.SetPasswordAPIView.as_view(), name='set-password'),
    path('update-password/', views.UpdatePasswordAPIView.as_view(), name='update-password'),
]

urlpatterns +=[
    path('devices/', DeviceRegisterCreateAPIView.as_view(), name='device-register'),
    path('devices/list/', DeviceListApiView.as_view(), name='device-list'),
]