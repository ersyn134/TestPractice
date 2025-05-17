from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from apps.quiz.forms import SessionForm
from apps.quiz.models import Question, SessionQuestion, Session, UserAnswer
import random

@login_required

def start_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user

            # Получаем время из формы, переводим в секунды
            duration_minutes = form.cleaned_data.get('duration_minutes') or 10
            session.duration = duration_minutes * 60

            session.save()

            question_count = int(request.POST.get('question_count'))
            mode = request.POST.get('mode')

            questions = Question.objects.filter(user=session.user)
            if mode == 'O':
                questions = questions.order_by('created_at')[:question_count]
            else:
                questions = questions.order_by('?')[:question_count]

            for i, question in enumerate(questions):
                SessionQuestion.objects.create(session=session, question=question, order=i)

            return redirect('session_question_view', session_id=session.id, index=0)

    else:
        form = SessionForm()
    return render(request, 'sessions/start_session.html', {'form': form})


@login_required
def session(request, session_id, index):
    session = Session.objects.get(id=session_id, user=request.user)

    if session.status == 'C':
        return redirect('session_complete_view', session_id=session.id)

    session_questions = SessionQuestion.objects.filter(session=session).order_by('order')

    time_elapsed = (now() - session.start_time).total_seconds()
    if session.duration and time_elapsed >= session.duration:
        auto_finish_session(session, request.user)
        return redirect('session_complete_view', session_id=session.id)

    if index < 0 or index >= session_questions.count():
        return redirect('session_complete_view', session_id=session.id)

    # Здесь замените строку
    # time_left = max(0, session.duration - time_elapsed) if session.duration else None
    # на
    time_elapsed = int((now() - session.start_time).total_seconds())
    time_left = max(0, session.duration - time_elapsed) if session.duration is not None else 0

    session_question = session_questions[index]
    question = session_question.question

    if request.method == 'GET':
        progress_percent = int((index + 1) / session_questions.count() * 100)

        return render(request, 'sessions/session_question.html', {
            'question': question,
            'current_index': index + 1,
            'total_questions': session_questions.count(),
            'is_last': index == session_questions.count() - 1,
            'progress_percent': progress_percent,
            'time_left': int(time_left),
        })

    elif request.method == 'POST':
        selected_option = request.POST.get('selected_option', '')
        is_correct = (selected_option == question.correct_option) if selected_option else False

        UserAnswer.objects.create(
            user=request.user,
            session=session,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )

        if index + 1 >= session_questions.count():
            return redirect('session_complete_view', session_id=session.id)
        else:
            return redirect('session_question_view', session_id=session.id, index=index + 1)
    elif request.method == 'POST':
        selected_option = request.POST.get('selected_option', '')
        is_correct = (selected_option == question.correct_option) if selected_option else False

        UserAnswer.objects.create(
            user=request.user,
            session=session,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        )

        if index + 1 >= session_questions.count():
            return redirect('session_complete_view', session_id=session.id)
        else:
            return redirect('session_question_view', session_id=session.id, index=index + 1)


def session_complete(request, session_id):
    session = Session.objects.get(id=session_id)
    session.end_time = now()
    session.status = 'C'
    session.save()

    answers = UserAnswer.objects.filter(session=session)
    correct_count = answers.filter(is_correct=True).count()
    total = answers.count()

    duration = (
        session.end_time -
        session.start_time).total_seconds()  # в секундах

    return render(request, 'sessions/session_complete.html', {
        'session': session,
        'correct_count': correct_count,
        'total': total,
        'duration': duration,
        'answers': answers,
    })

@login_required

def delete_session(request, session_id):
    session = Session.objects.get(id=session_id, user=request.user)
    if request.method == 'POST':
        session.delete()
        return redirect('user_sessions')
    return render(request,
                  'sessions/delete_session.html',
                  {'session': session})


def compare_session(request, session_id):
    current = Session.objects.get(id=session_id, user=request.user)
    others = Session.objects.filter(user=request.user).exclude(id=session_id)
    comparisons = []

    for s in others:
        total = UserAnswer.objects.filter(session=s).count()
        correct = UserAnswer.objects.filter(session=s, is_correct=True).count()
        percent = round((correct / total) * 100, 1) if total else 0
        comparisons.append({
            'session': s,
            'correct': correct,
            'total': total,
            'percent': percent,
        })

    current_correct = UserAnswer.objects.filter(session=current, is_correct=True).count()
    current_total = UserAnswer.objects.filter(session=current).count()
    current_percent = round((current_correct / current_total) * 100, 1) if current_total else 0

    return render(request, 'sessions/compare_session.html', {
        'current_session': current,
        'current_correct': current_correct,
        'current_total': current_total,
        'current_percent': current_percent,
        'comparisons': comparisons
    })



# views.py
@login_required
def user_sessions(request):
    sessions = Session.objects.filter(user=request.user).order_by('-created_at')
    completed_sessions = sessions.filter(status='C')
    latest_completed = completed_sessions.first() if completed_sessions.exists() else None
    return render(request, 'sessions/user_sessions.html', {
        'sessions': sessions,
        'latest_completed': latest_completed,
    })


@login_required
def repeat_session(request, session_id):
    old_session = Session.objects.get(id=session_id)
    new_session = Session.objects.create(
        user=request.user,
        mode=old_session.mode,
        question_count=old_session.question_count,
        name=old_session.name + " (повтор)",
        duration=old_session.duration  # добавьте это
    )

    old_questions = SessionQuestion.objects.filter(
        session=old_session).order_by('order')
    for i, sq in enumerate(old_questions):
        SessionQuestion.objects.create(
            session=new_session, question=sq.question, order=i)
    return redirect(
        'session_question_view',
        session_id=new_session.id,
        index=0)

def auto_finish_session(session, user):
    answered_q_ids = UserAnswer.objects.filter(session=session).values_list('question_id', flat=True)
    unanswered = SessionQuestion.objects.filter(session=session).exclude(question__id__in=answered_q_ids)

    for sq in unanswered:
        UserAnswer.objects.create(
            user=user,
            session=session,
            question=sq.question,
            selected_option='',  # Пусто — нет ответа
            is_correct=False
        )

    session.status = 'C'
    session.end_time = now()
    session.save()

