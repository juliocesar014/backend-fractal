from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class RoleTypes(models.TextChoices):
        ADMIN = "admin"
        PARTICIPANT = "participant"

    role = models.CharField(
        max_length=20, choices=RoleTypes.choices, default=RoleTypes.PARTICIPANT)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.username} with role {self.role}"


class Exam(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} (Correct: {self.is_correct})"
