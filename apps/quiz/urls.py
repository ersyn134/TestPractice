from django.urls import path
from apps.quiz.questions_view.views import (
    add_question,
    list_questions,
    edit_question,
    delete_question,
)
from apps.quiz.sessions_view.views import (
    start_session,
    session,
    session_complete,
    user_sessions,
    repeat_session, delete_session, compare_session
)

urlpatterns = [
    # Вопросы
    path('add_question/', add_question, name='question_add'),
    path('list_questions/', list_questions, name='questions_list'),
    path('edit_question/<int:id>/', edit_question, name='edit_question'),
    path('delete_question/<int:id>/', delete_question, name='delete_question'),

    # Сессии
    # Старт новой сессии
    path('start/', start_session, name='start_session'),

    # Просмотр вопроса сессии
    path('<int:session_id>/question/<int:index>/', session, name='session_question_view'),

    # Завершение сессии
    path('<int:session_id>/complete/', session_complete, name='session_complete_view'),

    # Повтор сессии
    path('<int:session_id>/repeat/', repeat_session, name='repeat_session'),

    # Удаление сессии
    path('<int:session_id>/delete/', delete_session, name='delete_session'),

    # Сравнение текущей сессии с прошлыми
    path('<int:session_id>/compare/', compare_session, name='compare_session'),

    # Список всех сессий пользователя
    path('', user_sessions, name='user_sessions'),

]
