from django.db import models
from .project import Project
from .channel import Channel

class Post(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PENDING = 'pending_review'
    STATUS_APPROVED = 'approved'
    STATUS_SCHEDULED = 'scheduled'
    STATUS_PUBLISHED = 'published'
    STATUS_ALL_PUBLISHED = 'all_published'

    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ALL_PUBLISHED, 'All Published'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    ai_generated = models.BooleanField(default=False)
    ai_model = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Post ({self.id})"


class PostSchedule(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="schedules")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name="schedules")
    scheduled_time = models.DateTimeField()
    published_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Schedule for Post {self.post_id} on Channel {self.channel_id}"