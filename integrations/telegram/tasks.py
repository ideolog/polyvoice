from celery import shared_task
import asyncio
from .service import send_message

@shared_task
def send_telegram_message_task(chat_id, text):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_message(chat_id, text))
    finally:
        loop.close()