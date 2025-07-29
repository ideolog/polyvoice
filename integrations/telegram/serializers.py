from rest_framework import serializers

class TelegramSendMessageSerializer(serializers.Serializer):
    chat_id = serializers.CharField()
    text = serializers.CharField()