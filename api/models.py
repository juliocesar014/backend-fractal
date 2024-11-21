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
