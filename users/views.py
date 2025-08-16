from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = []  # <— отключаем троттл для /api/me/

    def get(self, request):
        u = request.user
        plan = getattr(u, "plan", None)
        return Response({
            "id": u.id,
            "email": u.email,
            "api_key_present": bool(getattr(u, "api_key", "")),
            "plan": plan.name if plan else None,
            "photo_url": getattr(u, "photo_url", None),
        })

