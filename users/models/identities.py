from django.db import models
from django.conf import settings

class ExternalIdentity(models.Model):
    PROVIDER_TELEGRAM = "telegram"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="identities")
    provider = models.CharField(max_length=50)  # e.g. "telegram"
    external_id = models.CharField(max_length=255)  # stable TG user ID as string
    username = models.CharField(max_length=255, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    raw = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "external_id"], name="uniq_provider_external_id"),
        ]

    def __str__(self):
        return f"{self.provider}:{self.external_id} → {self.user.username}"