
from django.shortcuts import render, redirect
from quiz.forms import SessionForm
from quiz.models import Question, SessionQuestion

def start_session(request):
    return render(request, 'sessions/start_session.html')