from .serializers import TelegramSendMessageSerializer
from .tasks import send_telegram_message_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import SimpleRateThrottle
from urllib.parse import parse_qsl
from django.conf import settings
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
        api_key = None
        try:
            ei = ExternalIdentity.objects.select_related("user").get(provider="telegram", external_id=tg_id)
            api_key = getattr(ei.user, "api_key", None)
        except ExternalIdentity.DoesNotExist:
            pass

        # успех — вернём безопасные поля (без hash)
        user = {k: v for k, v in params.items() if k != "hash"}
        return Response({"ok": True, "user": user, "api_key": api_key}, status=status.HTTP_200_OK)
