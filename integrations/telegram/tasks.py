from django.conf import settings
from celery import shared_task
import httpx
from django.core.files.base import ContentFile
import mimetypes
import os


@shared_task(rate_limit="1/m", autoretry_for=(httpx.HTTPStatusError,), retry_backoff=True, max_retries=5)
def send_telegram_message_task(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    with httpx.Client(timeout=10) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()  # если Telegram вернёт ошибку, Celery сделает retry


@shared_task(autoretry_for=(httpx.HTTPStatusError,), retry_backoff=True, max_retries=5)
def download_telegram_avatar_task(ei_id: int) -> None:
    """
    Скачивает картинку по photo_url у ExternalIdentity и сохраняет её
    в поле avatar. Если photo_url не задан, ничего не делает.
    """
    from users.models.identities import ExternalIdentity

    try:
        identity = ExternalIdentity.objects.select_related('user').get(id=ei_id)
    except ExternalIdentity.DoesNotExist:
        return

    # Если у нас нет URL исходного фото, скачивать нечего
    if not identity.photo_url:
        return

    # Загружаем картинку с Telegram CDN
    with httpx.Client(timeout=10) as client:
        response = client.get(identity.photo_url)
        response.raise_for_status()

    content = response.content
    # Определяем расширение файла из Content-Type или из URL
    content_type = response.headers.get("Content-Type", "")
    ext = ""
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0]) or ""
    if not ext:
        # если не получилось — пробуем достать расширение из URL без query-параметров
        ext = os.path.splitext(identity.photo_url.split("?")[0])[1]
    # формируем имя файла
    filename = f"tg_avatar_{identity.external_id}{ext or '.jpg'}"

    # Сохраняем файл в поле avatar. save=True, чтобы сразу записать в базу.
    identity.avatar.save(filename, ContentFile(content), save=True)
