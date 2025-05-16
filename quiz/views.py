from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import QuestionForm

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
