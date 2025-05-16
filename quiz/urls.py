from django.urls import path
from .views import add_question
urlpatterns = [
    path('add_question/', add_question, name='question_add'),
]