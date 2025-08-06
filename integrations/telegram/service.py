from telegram import Bot
from telegram.constants import ParseMode
import asyncio
from django.conf import settings

async def send_message(chat_id, text):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=chat_id, text=text, parse_mode=ParseMode.HTML)