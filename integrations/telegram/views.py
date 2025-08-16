from .serializers import TelegramSendMessageSerializer
from .tasks import send_telegram_message_task, download_telegram_avatar_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle
from urllib.parse import parse_qsl
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .auth import validate_login_widget

class TelegramSendMessageView(APIView):
    def post(self, request):
        serializer = TelegramSendMessageSerializer(data=request.data)
        if serializer.is_valid():
            send_telegram_message_task.delay(
                chat_id=serializer.validated_data["chat_id"],
                text=serializer.validated_data["text"]
            )
            return Response({"status": "message queued"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TelegramLoginVerifyView(APIView):
    """
    Принимает JSON: {"search": "?id=...&first_name=...&hash=..."} или можно прислать чистую строку без "?"
    Возвращает {ok: true, user: {...}} при успехе
    """
    authentication_classes = []  # логин публичный
    permission_classes = []
    throttle_classes = []  # <-- отключаем лимиты для логина

    def post(self, request):
        search = request.data.get("search", "")
        if not isinstance(search, str):
            return Response({"ok": False, "error": "missing search"}, status=status.HTTP_400_BAD_REQUEST)

        if search.startswith("?"):
            search = search[1:]

        params = dict(parse_qsl(search, keep_blank_values=True))
        bot_token = settings.TELEGRAM_BOT_TOKEN

        if not validate_login_widget(params, bot_token):
            return Response({"ok": False, "error": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        # --- связываем с ExternalIdentity ---
        from users.models.identities import ExternalIdentity

        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")
        UserModel = get_user_model()

        # создаём или находим существующую ExternalIdentity
        identity, created = ExternalIdentity.objects.get_or_create(
            provider="telegram",
            external_id=tg_id,
            defaults={"raw": params},
        )
        if created:
            # если ExternalIdentity новая — создаём пользователя и связываем его
            user = UserModel.objects.create_user(
                username=f"tg_{tg_id}",
                password=UserModel.objects.make_random_password(),
            )
            identity.user = user

        # обновляем данные о пользователе Telegram
        identity.username = username or identity.username
        identity.photo_url = photo_url or identity.photo_url
        identity.raw = params
        identity.save()

        # ставим задачу на скачивание аватара, если фото есть
        if photo_url:
            download_telegram_avatar_task.delay(identity.id)

        # получаем api_key, если он уже был присвоен
        api_key = getattr(identity.user, "api_key", None)
        # формируем безопасные поля для фронта (без hash)
        safe_user = {k: v for k, v in params.items() if k != "hash"}
        # путь к локальному аватару, если он уже скачан
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        return Response(
            {"ok": True, "user": safe_user, "api_key": api_key, "avatar": avatar_url},
            status=status.HTTP_200_OK,
        )