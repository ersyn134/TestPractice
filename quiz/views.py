from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import QuestionForm
from .models import Question


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
    return render(request, 'add_question.html', {'form': form})

def list_questions(request):
    questions = Question.objects.all().filter(user=request.user)
    return render(request,'questions_list.html', {'questions': questions})

def edit_question(request, id):
    question = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = QuestionForm(instance=question)

    return render(request, 'edit_question.html', {'form': form})

def delete_question(request, id):
    question = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        question.delete()
        return redirect('home')

    return render(request, 'delete_question.html', {'question': question})