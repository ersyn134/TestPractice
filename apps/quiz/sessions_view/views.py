from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now

from apps.quiz.forms import SessionForm
from apps.quiz.models import Question, SessionQuestion, Session, UserAnswer
import random


@login_required
def start_session(request):
    """
    Создаёт сессию. В режиме 'V' выбирает один из 10 заранее созданных вариантов (is_variant=True).
    В других режимах — обычный режим с вопросами пользователя.
    """
    if request.method == 'POST':
        form = SessionForm(request.POST, user=request.user)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user

            duration_minutes = form.cleaned_data.get('duration_minutes') or 10
            session.duration = duration_minutes * 60
            session.save()

            mode = form.cleaned_data['mode']

            if mode == 'V':
                # Режим вариант: берем один из 10 вариантов с is_variant=True
                variants = Session.objects.filter(user=request.user, is_variant=True).order_by('?')[:1]
                if not variants.exists():
                    form.add_error(None, "У вас нет созданных вариантов для режима 'Variant'. Сначала создайте их.")
                    total_questions = Question.objects.filter(user=request.user).count()
                    return render(request, 'sessions/start_session.html', {
                        'form': form,
                        'total_questions': total_questions
                    })

                variant_session = variants.first()

                # Копируем вопросы из варианта в новую сессию
                variant_questions = SessionQuestion.objects.filter(session=variant_session).order_by('order')
                for idx, sq in enumerate(variant_questions):
                    SessionQuestion.objects.create(session=session, question=sq.question, order=idx)

                # Сохраняем количество вопросов из варианта
                session.question_count = variant_questions.count()
                session.save()

            else:
                # Режимы O и R — обычные вопросы
                question_count = form.cleaned_data['question_count']
                qs = Question.objects.filter(user=request.user)
                if mode == 'R':
                    qs = qs.order_by('?')[:question_count]
                else:
                    qs = qs.order_by('created_at')[:question_count]

                for idx, q in enumerate(qs):
                    SessionQuestion.objects.create(session=session, question=q, order=idx)

            return redirect('session_question_view', session_id=session.id, index=0)

    else:
        form = SessionForm(user=request.user)

    total_questions = Question.objects.filter(user=request.user).count()
    return render(request, 'sessions/start_session.html', {
        'form': form,
        'total_questions': total_questions,
    })


@login_required
def session(request, session_id, index):
    session = get_object_or_404(Session, id=session_id, user=request.user)

    # автозавершение по таймауту
    elapsed = (now() - session.start_time).total_seconds()
    if session.duration and elapsed >= session.duration:
        auto_finish_session(session, request.user)
        return redirect('session_complete_view', session_id=session.id)

    sqs = SessionQuestion.objects.filter(session=session).order_by('order')
    total = sqs.count()
    if index < 0 or index >= total:
        return redirect('session_complete_view', session_id=session.id)

    q = sqs[index].question

    # Собираем все тексты вариантов и перемешиваем их, если нужно:
    opts = q.all_options()
    if session.option_order == 'R':
        random.shuffle(opts)

    # Если GET — рендерим
    if request.method == 'GET':
        progress = int((index+1)/total * 100)
        time_left = max(0, int(session.duration - elapsed)) if session.duration else None

        return render(request, 'sessions/session_question.html', {
            'question': q,
            'options': opts,
            'current_index': index+1,
            'total_questions': total,
            'is_last': index == total-1,
            'progress_percent': progress,
            'time_left': time_left,
            'session_id': session.id,
            'next_index': index+1,
        })

    # POST — сохраняем выбранный текст
    selected_text = request.POST.get('selected_text', '')
    is_correct = (selected_text == q.correct_text)

    UserAnswer.objects.create(
        user=request.user,
        session=session,
        question=q,
        selected_text=selected_text,
        is_correct=is_correct
    )

    if index+1 >= total:
        return redirect('session_complete_view', session_id=session.id)
    return redirect('session_question_view', session_id=session.id, index=index+1)


@login_required
def session_complete(request, session_id):
    """
    Итоговая страница. Выводим список UserAnswer, сравниваем
    selected_text с correct_text и подсвечиваем.
    """
    session = get_object_or_404(Session, id=session_id, user=request.user)
    if session.status != 'C':
        session.end_time = now()
        session.status = 'C'
        session.save()

    answers = UserAnswer.objects.filter(session=session)
    correct = answers.filter(is_correct=True).count()
    total = answers.count()
    duration = ((session.end_time - session.start_time).total_seconds()
                if session.end_time and session.start_time else 0)

    return render(request, 'sessions/session_complete.html', {
        'session': session,
        'answers': answers,
        'correct_count': correct,
        'total': total,
        'duration': duration,
    })


@login_required
def auto_finish_session(session, user):
    """Помечаем все неотвеченные вопросы неверными и закрываем сессию."""
    answered_ids = UserAnswer.objects.filter(
        session=session).values_list('question_id', flat=True)
    unanswered = SessionQuestion.objects.filter(
        session=session).exclude(question__id__in=answered_ids)
    for sq in unanswered:
        UserAnswer.objects.create(
            user=user, session=session,
            question=sq.question,
            selected_text='', is_correct=False
        )
    session.status = 'C'
    session.end_time = now()
    session.save()


@login_required
def delete_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, user=request.user)
    if request.method == 'POST':
        session.delete()
        return redirect('user_sessions')
    return render(request, 'sessions/delete_session.html', {
        'session': session
    })


@login_required
def compare_session(request, session_id):
    current = get_object_or_404(Session, id=session_id, user=request.user)
    others  = Session.objects.filter(user=request.user).exclude(id=session_id)
    comps = []
    for s in others:
        tot = UserAnswer.objects.filter(session=s).count()
        cor = UserAnswer.objects.filter(session=s, is_correct=True).count()
        comps.append({
            'session': s,
            'correct': cor,
            'total': tot,
            'percent': round(cor / tot * 100, 1) if tot else 0
        })
    cur_cor = UserAnswer.objects.filter(session=current, is_correct=True).count()
    cur_tot = UserAnswer.objects.filter(session=current).count()
    cur_pct = round(cur_cor / cur_tot * 100, 1) if cur_tot else 0

    return render(request, 'sessions/compare_session.html', {
        'current_session': current,
        'current_correct': cur_cor,
        'current_total': cur_tot,
        'current_percent': cur_pct,
        'comparisons': comps
    })


@login_required
def user_sessions(request):
    sessions = Session.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'sessions/user_sessions.html', {
        'sessions': sessions
    })


@login_required
def repeat_session(request, session_id):
    old = get_object_or_404(Session, id=session_id, user=request.user)
    new = Session.objects.create(
        user=request.user,
        mode=old.mode,
        option_order=old.option_order,
        question_count=old.question_count,
        name=old.name + ' (повтор)',
        duration=old.duration
    )
    for sq in SessionQuestion.objects.filter(session=old).order_by('order'):
        SessionQuestion.objects.create(
            session=new, question=sq.question, order=sq.order
        )
    return redirect('session_question_view',
                    session_id=new.id, index=0)
