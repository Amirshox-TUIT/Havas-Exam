from django.urls import path
from .. import views

app_name = 'questionnaires'

urlpatterns = [
    path('', views.QuestionnaireListCreateAPIView.as_view(), name='questionnaires_list_create'),
    path("<int:questionnaire_id>/questions/", views.QuestionnaireQuestionsListAPIView.as_view()),
    path("vote/", views.VoteCreateAPIView.as_view()),
]
