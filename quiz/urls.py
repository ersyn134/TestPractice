from django.urls import path
from quiz.questions_view.views import add_question,list_questions,edit_question,delete_question
from quiz.sessions_view.views import start_session
urlpatterns = [
    path('add_question/', add_question, name='question_add'),
    path('list_questions/', list_questions, name='questions_list'),
    path('edit_question/<int:id>', edit_question, name='edit_question'),
    path('delete_question/<int:id>', delete_question, name='delete_question'),
    path('start_session/', start_session, name='start_session'),


]