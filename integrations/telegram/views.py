import os
import hmac
import hashlib
from urllib.parse import parse_qsl
import logging
import httpx

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import TelegramSendMessageSerializer
from .tasks import send_telegram_message_task
from .auth import validate_login_widget, validate_miniapp
from users.models.identities import ExternalIdentity

logger = logging.getLogger(__name__)


class TelegramSendMessageView(APIView):
    """Send a message via bot (now protected)."""
    permission_classes = [IsAuthenticated]

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
    """Verify Telegram login (both Widget and MiniApp)."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def post(self, request):
        search = request.data.get("search", "")
        source = request.data.get("source", "widget")

        logger.debug("== TelegramLoginVerifyView ==")
        logger.debug("source=%s", source)
        logger.debug("raw search=%s", search)

        if not isinstance(search, str):
            return Response({"ok": False, "error": "missing search"}, status=status.HTTP_400_BAD_REQUEST)

        if search.startswith("?"):
            search = search[1:]

        from urllib.parse import unquote
        search = unquote(search)

        params = dict(parse_qsl(search, keep_blank_values=True))

        # 🔹 MiniApp: initData содержит поле user в JSON
        if source == "miniapp" and "user" in params:
            import json
            try:
                user_data = json.loads(params["user"])
                for k, v in user_data.items():
                    params[str(k)] = str(v)
            except Exception as e:
                logger.warning("Failed to parse user JSON from miniapp initData: %s", e)

        logger.debug("params=%s", params)

        bot_token = settings.TELEGRAM_BOT_TOKEN

        if source == "miniapp":
            valid = validate_miniapp(params, bot_token)
        else:
            valid = validate_login_widget(params, bot_token)

        if not valid:
            return Response({"ok": False, "error": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        UserModel = get_user_model()
        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")

        try:
            identity = ExternalIdentity.objects.get(provider="telegram", external_id=tg_id)
            user = identity.user
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

        # --- sync fields ---
        identity.username = username or identity.username
        identity.raw = params

        # --- avatar download ---
        needs_download = False
        if photo_url and photo_url != identity.photo_url:
            identity.photo_url = photo_url
            needs_download = True

        try:
            if not identity.avatar or not identity.avatar.name:
                needs_download = True
            else:
                if not os.path.exists(identity.avatar.path):
                    needs_download = True
        except Exception:
            needs_download = True

        if needs_download and identity.photo_url:
            try:
                response = httpx.get(identity.photo_url, timeout=10, follow_redirects=True)
                if response.status_code == 200 and response.content:
                    filename = f"avatars/tg_{tg_id}.jpg"
                    identity.avatar.save(filename, ContentFile(response.content), save=True)
                    logger.info(f"Saved Telegram avatar for %s", tg_id)
                else:
                    logger.warning("Empty/failed response when fetching avatar for %s", tg_id)
            except Exception as e:
                logger.warning("Failed to fetch Telegram avatar for %s: %s", tg_id, e)

        identity.save()

        # --- ensure api_key exists ---
        if not getattr(user, "api_key", None):
            user.api_key = UserModel.objects.make_random_password(length=40)
            user.save()

        safe_user = {k: v for k, v in params.items() if k != "hash"}
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        return Response(
            {
                "ok": True,
                "user": safe_user,
                "api_key": user.api_key,
                "avatar": avatar_url,
            },
            status=status.HTTP_200_OK,
        )

