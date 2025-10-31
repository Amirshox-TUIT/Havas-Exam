from django.urls import path

from apps.history import views

app_name = 'history'

urlpatterns = [
    path('', views.HistoryListAPIView.as_view(), name='list'),
    path('<int:pk>/', views.HistoryRetrieveAPIView.as_view(), name='retrieve'),
]