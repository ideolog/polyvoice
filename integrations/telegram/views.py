import os
from .serializers import TelegramSendMessageSerializer
from .tasks import send_telegram_message_task
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from urllib.parse import parse_qsl
from django.conf import settings
from django.contrib.auth import get_user_model
from .auth import validate_login_widget
from users.models.identities import ExternalIdentity
import httpx
from django.core.files.base import ContentFile
import logging

logger = logging.getLogger(__name__)


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
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

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

        UserModel = get_user_model()

        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")

        try:
            identity = ExternalIdentity.objects.get(provider="telegram", external_id=tg_id)
        except ExternalIdentity.DoesNotExist:
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

        identity.username = username or identity.username
        identity.raw = params

        # --- аватар ---
        needs_download = False

        if photo_url and photo_url != identity.photo_url:
            identity.photo_url = photo_url
            needs_download = True

        try:
            if not identity.avatar or not identity.avatar.name:
                needs_download = True
            else:
                avatar_path = identity.avatar.path
                if not os.path.exists(avatar_path):
                    needs_download = True
        except Exception:
            needs_download = True

        if needs_download and identity.photo_url:
            try:
                response = httpx.get(identity.photo_url, timeout=10, follow_redirects=True)
                if response.status_code == 200 and response.content:
                    filename = f"avatars/tg_{tg_id}.jpg"
                    identity.avatar.save(filename, ContentFile(response.content), save=True)
                    logger.info(f"Saved Telegram avatar for {tg_id}")
                else:
                    logger.warning(f"Empty/failed response when fetching avatar for {tg_id}")
            except Exception as e:
                logger.warning(f"Failed to fetch Telegram avatar for {tg_id}: {e}")

        identity.save()

        api_key = getattr(identity.user, "api_key", None)
        safe_user = {k: v for k, v in params.items() if k != "hash"}
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        return Response(
            {"ok": True, "user": safe_user, "api_key": api_key, "avatar": avatar_url},
            status=status.HTTP_200_OK,
        )
