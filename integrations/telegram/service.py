from telegram import Bot
from django.conf import settings
import asyncio

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)
