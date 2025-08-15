import httpx
from django.conf import settings

API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"

def send_message(chat_id: str, text: str):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    with httpx.Client(timeout=15) as client:
        r = client.post(API_URL, json=payload)
        try:
            data = r.json()
        except Exception:
            data = {"non_json_body": r.text}
        print(f"[TG SEND] status={r.status_code} resp={data}")  # временный лог
        r.raise_for_status()
        # если Telegram вернул ok: false — поднимем ошибку для Celery логов
        if isinstance(data, dict) and not data.get("ok", True):
            raise RuntimeError(f"Telegram error: {data}")
        return data