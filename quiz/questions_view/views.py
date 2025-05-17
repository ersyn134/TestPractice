from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from quiz.forms import QuestionForm
from quiz.models import Question


@login_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user  # Привязываем к пользователю
            question.save()
            return redirect('home')
    else:
        form = QuestionForm()
    return render(request, 'questions/add_question.html', {'form': form})

def list_questions(request):
    search_query = request.GET.get('q', '')
    date_filter = request.GET.get('date', '')

    questions = Question.objects.filter(user=request.user)

    if search_query:
        questions = questions.filter(text__icontains=search_query)

    if date_filter:
        questions = questions.filter(created_at__date=date_filter)

    # Пагинация
    paginator = Paginator(questions.order_by('created_at'), 5)  # 5 вопросов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'questions/questions_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'date_filter': date_filter,
    })

def edit_question(request, id):
    question = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'questions/edit_question.html', {'form': form})

def delete_question(request, id):
    question = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        question.delete()
        return redirect('home')

    return render(request, 'questions/delete_question.html', {'question': question})