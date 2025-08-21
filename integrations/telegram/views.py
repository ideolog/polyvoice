import os
import hmac
import hashlib
from urllib.parse import parse_qsl, unquote
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
    """Verify Telegram login (supports both Widget and MiniApp)."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def post(self, request):
        source = request.data.get("source", "widget")
        bot_token = settings.TELEGRAM_BOT_TOKEN

        print("\n==============================")
        print("== TelegramLoginVerifyView ==")
        print("Source:", source)

        raw = request.data.get("raw")
        unsafe = request.data.get("unsafe")
        print("raw =", raw)
        print("unsafe =", unsafe)

        params = {}

        # ---------------------------------
        # MiniApp branch
        # ---------------------------------
        if source == "miniapp":
            raw = request.data.get("raw", "")
            if not raw:
                print("❌ Missing raw param for miniapp")
                return Response({"ok": False, "error": "missing raw"}, status=status.HTTP_400_BAD_REQUEST)

            from urllib.parse import parse_qsl
            params_initial = dict(parse_qsl(raw, keep_blank_values=True))
            print("miniapp.params.initial =", params_initial)

            # Validate ONLY initial params (user still JSON string!)
            valid = validate_miniapp(params_initial, bot_token)
            print("validation_result (miniapp initial) =", valid)

            if not valid:
                return Response({"ok": False, "error": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

            # Expand with unsafe.user only AFTER validation
            params = params_initial.copy()
            if isinstance(unsafe, dict) and "user" in unsafe:
                for k, v in unsafe["user"].items():
                    params[str(k)] = str(v)
            print("miniapp.params.with_user =", params)


        print("final.params =", params)
        print("BOT_TOKEN (prefix) =", settings.TELEGRAM_BOT_TOKEN[:10])

        # ---------------------------------
        # User / identity handling
        # ---------------------------------
        UserModel = get_user_model()
        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")

        print(f"Looking up Telegram user {username} ({tg_id})")

        try:
            identity = ExternalIdentity.objects.get(provider="telegram", external_id=tg_id)
            user = identity.user
            print(f"✅ Existing Telegram user found: {username} ({tg_id})")
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
            print(f"🆕 Registered new Telegram user: {username} ({tg_id})")

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
                print(f"Fetching avatar from {identity.photo_url}")
                response = httpx.get(identity.photo_url, timeout=10, follow_redirects=True)
                if response.status_code == 200 and response.content:
                    filename = f"avatars/tg_{tg_id}.jpg"
                    identity.avatar.save(filename, ContentFile(response.content), save=True)
                    print(f"✅ Saved Telegram avatar for {tg_id}")
                else:
                    print(f"⚠️ Empty/failed response when fetching avatar for {tg_id}")
            except Exception as e:
                print(f"❌ Failed to fetch Telegram avatar for {tg_id}: {e}")

        identity.save()

        # --- ensure api_key exists ---
        if not getattr(user, "api_key", None):
            user.api_key = UserModel.objects.make_random_password(length=40)
            user.save()
            print(f"Generated new API key for {username} ({tg_id})")

        safe_user = {k: v for k, v in params.items() if k not in ("hash", "signature")}
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        print(f"🎉 Telegram auth SUCCESSFUL: {username} ({tg_id})")
        print("==============================\n")

        return Response(
            {
                "ok": True,
                "user": safe_user,
                "api_key": user.api_key,
                "avatar": avatar_url,
            },
            status=status.HTTP_200_OK,
        )

class TelegramWidgetLoginVerifyView(APIView):
    """Verify Telegram login for Widget (GET with query string)."""
    authentication_classes = []
    permission_classes = []
    throttle_classes = []

    def get(self, request):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        search = request.META.get("QUERY_STRING", "")
        search = unquote(search)
        params = dict(parse_qsl(search, keep_blank_values=True))

        if not validate_login_widget(params, bot_token):
            return Response({"ok": False, "error": "invalid signature"}, status=status.HTTP_401_UNAUTHORIZED)

        return self._finalize(request, params)


    # --- shared logic ---
    def _finalize(self, request, params: dict):
        UserModel = get_user_model()
        tg_id = str(params.get("id", ""))
        username = params.get("username")
        photo_url = params.get("photo_url")

        # find or create user
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

        # sync identity fields
        identity.username = username or identity.username
        identity.raw = params

        # download avatar if needed
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
            except Exception as e:
                print(f"❌ Failed to fetch Telegram avatar for {tg_id}: {e}")

        identity.save()

        # ensure api_key
        if not getattr(user, "api_key", None):
            user.api_key = UserModel.objects.make_random_password(length=40)
            user.save()

        safe_user = {k: v for k, v in params.items() if k not in ("hash", "signature")}
        avatar_url = request.build_absolute_uri(identity.avatar.url) if identity.avatar else None

        return Response(
            {"ok": True, "user": safe_user, "api_key": user.api_key, "avatar": avatar_url},
            status=status.HTTP_200_OK,
        )





