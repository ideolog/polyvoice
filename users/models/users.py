from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import UserManager
from users.models.plans import Plan

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    plan = models.ForeignKey(
        Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email