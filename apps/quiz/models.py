from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
# Create your models here.


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)

    CHOICES = [
        ('A', 'Variant A'),
        ('B', 'Variant B'),
        ('C', 'Variant C'),
        ('D', 'Variant D'),
    ]
    correct_text = models.CharField(
        max_length=255,
        default='',

        help_text="Здесь хранится ровно тот текст, который является правильным"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)
    def all_options(self):
        return [
            self.option_a,
            self.option_b,
            self.option_c,
            self.option_d,
        ]
    def __str__(self):
        return self.text


class Session(models.Model):
    MODE_CHOICES = [('O', 'Порядок вопросов'), ('R', 'Случайно вопросы'),('V','Variant')]
    OPTION_ORDER_CHOICES = [('O', 'По порядку'), ('R', 'Случайно')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='Без названия')
    mode = models.CharField(max_length=1, choices=MODE_CHOICES, default='O')
    question_count = models.PositiveIntegerField(default=0)
    option_order = models.CharField(
        max_length=1,
        choices=OPTION_ORDER_CHOICES,
        default='O',
        help_text="В каком порядке показывать варианты ответа"
    )
    duration = models.PositiveIntegerField(default=0, help_text="Длительность сессии в секундах")
    start_time = models.DateTimeField(default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=1, choices=[('O','Opened'),('C','Closed')], default='O')
    created_at = models.DateTimeField(auto_now_add=True)
    is_variant = models.BooleanField(default=False)


    def __str__(self):
        return f"Session {self.id} — {self.user.username}"

class SessionQuestion(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()


# Ответ пользователя в рамках конкретной сессии


class UserAnswer(models.Model):
    CHOICES = [
        ('A', 'Variant A'),
        ('B', 'Variant B'),
        ('C', 'Variant C'),
        ('D', 'Variant D'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_text = models.CharField(max_length=255,default='')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{
            self.user.username} answered {
            self.selected_text} on {
            self.question.id}"
