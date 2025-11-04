from django.urls import path

from apps.admins.views import recipes, questionnaire
from apps.admins.views import users

app_name = 'admins'

urlpatterns = [
    path('users/', users.UsersListAPIView.as_view(), name='users_list'),
    path('users/<int:pk>/', users.UserDetailAPIView.as_view(), name='user_detail'),
    path('users/<int:pk>/devices/<int:id>/', users.DeviceDestroyAPIView.as_view(), name='user_devices'),
    path('users/statistics/', users.UserStatisticsAPIView.as_view(), name='users-statistics'),
    path('recipes/<int:pk>/', recipes.RecipeRetrieveUpdateDestroyAPIView.as_view(), name='recipes_detail'),
    path('recipes/', recipes.RecipeListCreateAPIView.as_view(), name='recipes_list'),
    path('recipes/<int:pk>/ingredients/', recipes.IngredientsListCreateAPIView.as_view(), name='recipes_ingredients'),
    path('recipes/<int:pk>/ingredients/<int:id>/', recipes.IngredientsRetrieveUpdateDestroyAPIView.as_view(), name='recipes_ingredients_detail'),
    path('recipes/<int:pk>/preparationsteps/', recipes.PreparationStepsListCreateAPIView.as_view(), name='recipes_preparation'),
    path('recipes/<int:pk>/preparationsteps/<int:id>/', recipes.PreparationStepsRetrieveUpdateDestroyAPIView.as_view(), name='recipes_preparation_detail'),
    path('questionnaires/<int:pk>/', questionnaire.QuestionnaireDetailAPIView.as_view(), name='questionnaire_detail'),
    path("questionnaires/<int:questionnaire_id>/questions/", questionnaire.QuestionCreateAPIView.as_view()),
    path("questions/<int:pk>/", questionnaire.QuestionRetrieveUpdateDestroyAPIView.as_view()),
    path("questions/<int:question_id>/answers/", questionnaire.AnswerCreateAPIView.as_view()),
    path("answers/<int:pk>/", questionnaire.AnswerRetrieveUpdateDestroyAPIView.as_view()),
]