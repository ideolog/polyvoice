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
    Принимает JSON: {"search": "?id=...&first_name=...&hash=..."}
    Возвращает {ok: true, user: {...}} при успехе
    """
    authentication_classes = []  # логин публичный
    permission_classes = []
    throttle_classes = []  # отключаем лимиты для логина

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

        from users.models.identities import ExternalIdentity
        UserModel = get_user_model()

        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")

        # пробуем найти существующую запись по tg_id
        try:
            identity = ExternalIdentity.objects.get(provider="telegram", external_id=tg_id)
            created = False
        except ExternalIdentity.DoesNotExist:
            # создаём пользователя и identity
            user = UserModel.objects.create_user(
                username=f"tg_{tg_id}",
                password=UserModel.objects.make_random_password(),
                email=None,
            )
            identity = ExternalIdentity.objects.create(
                provider="telegram",
                external_id=tg_id,
                user=user,
                raw=params,
            )
            created = True

        # обновляем метаданные (даже если запись старая)
        identity.username = username or identity.username
        identity.photo_url = photo_url or identity.photo_url
        identity.raw = params
        identity.save()

        # ставим задачу на скачивание аватарки
        if photo_url:
            download_telegram_avatar_task.delay(identity.id)

        api_key = getattr(identity.user, "api_key", None)
        safe_user = {k: v for k, v in params.items() if k != "hash"}
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        return Response(
            {"ok": True, "user": safe_user, "api_key": api_key, "avatar": avatar_url},
            status=status.HTTP_200_OK,
        )

