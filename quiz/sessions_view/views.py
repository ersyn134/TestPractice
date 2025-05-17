
from django.shortcuts import render, redirect
from quiz.forms import SessionForm
from quiz.models import Question, SessionQuestion
import random


def start_session(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            name = request.POST.get('name')
            mode = request.POST.get('mode')
            question_count = int(request.POST.get('question_count'))
            session.user = request.user
            session.save()
            questions = Question.objects.all().filter(user=session.user)
            if mode == 'O':
                questions = questions.order_by('created_at')[:question_count]
            else:
                questions = questions.order_by('?')[:question_count]

            for i, question in enumerate(questions):
                SessionQuestion.objects.create(
                    session=session, question=question, order=i)
            return redirect('home')
    else:
        form = SessionForm()
    return render(request, 'sessions/start_session.html', {'form': form})
