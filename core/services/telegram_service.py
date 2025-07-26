from telegram import Bot
from django.conf import settings

def send_message(chat_id, text="Hello from PolyVoice!"):
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=chat_id, text=text)