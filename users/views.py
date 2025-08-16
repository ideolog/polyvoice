from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from users.models.identities import ExternalIdentity

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []

    def get(self, request):
        u = request.user
        plan = getattr(u, "plan", None)
        # ищем Telegram‑идентичность пользователя
        identity = u.identities.filter(provider="telegram").first()
        avatar_url = None
        if identity and identity.avatar:
            # строим абсолютный URL для аватара
            avatar_url = request.build_absolute_uri(identity.avatar.url)

        return Response({
            "id": u.id,
            "email": u.email,
            "api_key_present": bool(getattr(u, "api_key", "")),
            "plan": plan.name if plan else None,
            "avatar": avatar_url,
        })