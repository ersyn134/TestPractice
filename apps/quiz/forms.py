from django import forms
from .models import Question,Session

from django import forms
from .models import Question

class QuestionForm(forms.ModelForm):
    #  выпадающий список по текстам option_*
    correct_text = forms.ChoiceField(label="Правильный ответ")

    class Meta:
        model = Question
        fields = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows':3}),
            'option_a': forms.TextInput(attrs={'class':'form-control'}),
            'option_b': forms.TextInput(attrs={'class':'form-control'}),
            'option_c': forms.TextInput(attrs={'class':'form-control'}),
            'option_d': forms.TextInput(attrs={'class':'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # составляем список вариантов из полей модели
        opts = [
            (self.instance.option_a, self.instance.option_a),
            (self.instance.option_b, self.instance.option_b),
            (self.instance.option_c, self.instance.option_c),
            (self.instance.option_d, self.instance.option_d),
        ]
        if not self.instance.pk:
            opts = [('', '— сначала заполните варианты —')]
        self.fields['correct_text'].choices = opts
        self.fields['correct_text'].widget.attrs.update({'class':'form-select'})

class SessionForm(forms.ModelForm):
    duration_minutes = forms.IntegerField(
            label='Время (минуты)', min_value=1, max_value=180, initial=10
        )

    class Meta:
            model = Session
            fields = ['name', 'mode', 'question_count', 'option_order']
            widgets = {
                'name': forms.TextInput(attrs={'class': 'form-control'}),
                'mode': forms.Select(attrs={'class': 'form-select'}),
                'question_count': forms.NumberInput(attrs={'class': 'form-control'}),
                'option_order': forms.Select(attrs={'class': 'form-select'}),
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