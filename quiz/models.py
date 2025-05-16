from django.db import models
from django.contrib.auth.models import User
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
    correct_option = models.CharField(max_length=1, choices=CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.text


class Session(models.Model):
    MODE_CHOICES = [
        ('O', 'Order'),
        ('R', 'Random'),
    ]
    STATUS_CHOICES = [
        ('O', 'Opened'),
        ('C', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=1, choices=MODE_CHOICES)
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='O')

    def __str__(self):
        return f"Session {self.pk} — {self.user.username}"

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
    selected_option = models.CharField(max_length=1, choices=CHOICES)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{
            self.user.username} answered {
            self.selected_option} on {
            self.question.id}"
