from django import forms
from .models import Question,Session

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'option_a': forms.TextInput(attrs={'class': 'form-control'}),
            'option_b': forms.TextInput(attrs={'class': 'form-control'}),
            'option_c': forms.TextInput(attrs={'class': 'form-control'}),
            'option_d': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
        }

class SessionForm(forms.ModelForm):
    duration_minutes = forms.IntegerField(
        label='Время на тренировку (минуты)',
        min_value=1,
        max_value=180,
        required=False,
        initial=10
    )
    class Meta:
        model = Session
        fields = ['mode', 'question_count','name']
        widgets = {
            'mode': forms.Select(attrs={'class': 'form-control'}),
            'question_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # получаем пользователя из view
        super().__init__(*args, **kwargs)

    def clean_question_count(self):
        count = self.cleaned_data['question_count']
        if self.user:
            available = Question.objects.filter(user=self.user).count()
            if count > available:
                raise forms.ValidationError(f"У вас только {available} вопросов.")
        return count