from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TelegramSendMessageSerializer
from .service import send_message  # async функция
import asyncio


class TelegramSendMessageView(APIView):
    def post(self, request):
        serializer = TelegramSendMessageSerializer(data=request.data)
        if serializer.is_valid():
            try:
                asyncio.run(send_message(
                    chat_id=serializer.validated_data["chat_id"],
                    text=serializer.validated_data["text"]
                ))
                return Response({"status": "message sent"}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)