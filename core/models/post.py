

from django.db import models
from .project import Project
from .channel import Channel

class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending_review'
    STATUS_APPROVED = 'approved'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="posts")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="posts", null=True, blank=True)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    scheduled_time = models.DateTimeField(blank=True, null=True)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post ({self.status}) for {self.project.name}"