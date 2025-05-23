from django.contrib import admin
from .models import Question, Session, UserAnswer,SessionQuestion

# Register your models here.



@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'mode', 'status')
    list_filter = ('status', 'mode', 'created_at')
    search_fields = ('user__username',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'text',
        'correct_text',
        'created_at'
    )
    search_fields = ('text',)
    list_filter = ('user',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'session', 'question',
        'selected_text',
        'is_correct'
    )
    list_filter = ('is_correct',)
    search_fields = ('user__username','question__text')

@admin.register(SessionQuestion)
class SessionQuestionAdmin(admin.ModelAdmin):
    list_display = ('session','question','order')
