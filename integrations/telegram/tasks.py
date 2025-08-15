from celery import shared_task
import httpx
from django.conf import settings

@shared_task(rate_limit="1/m", autoretry_for=(httpx.HTTPStatusError,), retry_backoff=True, max_retries=5)
def send_telegram_message_task(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    with httpx.Client(timeout=10) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()  # если Telegram вернёт ошибку, Celery сделает retry