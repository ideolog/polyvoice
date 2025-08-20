# users/auth.py
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions

class ApiKeyAuthentication(BaseAuthentication):
    """
    Простая аутентификация по заголовку X-API-Key.
    Используется для miniapp, когда мы логинимся через Telegram.
    """
    keyword = "X-API-Key"

    def authenticate(self, request):
        api_key = request.headers.get(self.keyword)
        if not api_key:
            return None  # вернём None → другие классы аутентификации могут сработать

        User = get_user_model()
        try:
            user = User.objects.get(api_key=api_key, is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API key")

        return (user, None)
