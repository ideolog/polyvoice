from django.db import models

class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    messages_per_minute = models.PositiveIntegerField(default=1)
    messages_per_day = models.PositiveIntegerField(default=1440)  # 1 msg/min * 24h

    def __str__(self):
        return self.name