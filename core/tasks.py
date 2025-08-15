# core/tasks.py
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from core.models import PostSchedule, Post, Channel
from integrations.telegram.tasks import send_telegram_message_task
import logging
logger = logging.getLogger(__name__)

BATCH_SIZE = 100  # защита от лавины

@shared_task(name="core.dispatch_due_schedules")
def dispatch_due_schedules():
    now = timezone.now()
    sent = 0
    with transaction.atomic():
        qs = (
            PostSchedule.objects
            .select_for_update(skip_locked=True)
            .select_related("post", "channel")
            .filter(
                published_at__isnull=True,
                scheduled_time__lte=now,
                post__status__in=[Post.STATUS_APPROVED, Post.STATUS_SCHEDULED],
            )
            .order_by("scheduled_time")[:BATCH_SIZE]
        )
        items = list(qs)

        for sch in items:
            # пока поддерживаем только телеграм
            if sch.channel.type == Channel.TELEGRAM and sch.channel.external_id:
                send_telegram_message_task.delay(
                    chat_id=sch.channel.external_id,
                    text=sch.post.content,
                )
                # фиксируем факт отправки в очередь
                sch.published_at = now
                sch.save(update_fields=["published_at"])
                # Update related Post status
                post = sch.post
                has_unpublished = PostSchedule.objects.filter(post=post, published_at__isnull=True).exists()
                if not has_unpublished:
                    post.status = Post.STATUS_ALL_PUBLISHED
                else:
                    post.status = Post.STATUS_PUBLISHED
                post.save(update_fields=["status"])
                logger.info("Post %s -> %s (remaining_unpublished=%s)",
                            sch.post_id, post.status,
                            post.schedules.filter(published_at__isnull=True).exists())
                sent += 1
    return sent