from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from apps.quiz.models import Question
from apps.quiz.forms import QuestionForm
@login_required
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.user = request.user
            q.save()
            return redirect('questions_list')
    else:
        form = QuestionForm()
    return render(request, 'questions/add_question.html', {'form': form})

@login_required
def edit_question(request, id):
    q = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=q)
        if form.is_valid():
            form.save()
            return redirect('questions_list')
    else:
        form = QuestionForm(instance=q)
    return render(request, 'questions/edit_question.html', {'form': form})

@login_required
def delete_question(request, id):
    q = get_object_or_404(Question, id=id, user=request.user)
    if request.method == 'POST':
        q.delete()
        return redirect('questions_list')
    return render(request, 'questions/delete_question.html', {'question': q})

@login_required
def list_questions(request):
    qs = Question.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'questions/questions_list.html', {'questions': qs})
