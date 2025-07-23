

from django.db import models
from .project import Project

class Channel(models.Model):
    TELEGRAM = 'telegram'
    TWITTER = 'twitter'
    LINKEDIN = 'linkedin'
    CHANNEL_TYPES = [
        (TELEGRAM, 'Telegram'),
        (TWITTER, 'Twitter'),
        (LINKEDIN, 'LinkedIn'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="channels")
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=CHANNEL_TYPES)
    credentials = models.JSONField(blank=True, null=True)  # API токен и доп. настройки
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.type})"