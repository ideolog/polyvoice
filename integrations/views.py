from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from integrations import send_telegram_message

class SendTelegramMessageView(APIView):
    def post(self, request):
        chat_id = request.data.get("chat_id")
        text = request.data.get("text")

        if not chat_id or not text:
            return Response({"detail": "chat_id and text are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            send_telegram_message(chat_id=chat_id, text=text)
            return Response({"detail": "Message sent."})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)