from django.urls import path

from apps.recipes import views

app_name = 'recipes'

urlpatterns = [
    path('', views.RecipesListAPI.as_view(), name='list'),
    path('<int:pk>/', views.RecipeDetailAPI.as_view(), name='detail'),
    path('<int:pk>/review/', views.RecipeReviewCreateAPIView.as_view(), name='review'),
    path('<int:pk>/ingredients/', views.IngredientsToProductBulkCreateAPIView.as_view(), name='ingredients'),
]