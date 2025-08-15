from rest_framework.throttling import SimpleRateThrottle

class TelegramPerChatThrottle(SimpleRateThrottle):
    scope = "telegram_send"

    def get_cache_key(self, request, view):
        data = request.data or {}
        chat_id = data.get("chat_id") or request.query_params.get("chat_id")
        if not chat_id:
            return None
        return f"throttle:telegram_send:{chat_id}"