from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TelegramSendMessageSerializer
from .service import send_message

class TelegramSendMessageView(APIView):
    def post(self, request):
        serializer = TelegramSendMessageSerializer(data=request.data)
        if serializer.is_valid():
            send_message(
                chat_id=serializer.validated_data["chat_id"],
                text=serializer.validated_data["text"]
            )
            return Response({"status": "message sent"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)