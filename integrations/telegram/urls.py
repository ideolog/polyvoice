from django.urls import path
from .views import TelegramSendMessageView, TelegramLoginVerifyView, TelegramWidgetLoginVerifyView

urlpatterns = [
    path("send/", TelegramSendMessageView.as_view(), name="telegram-send-message"),
    path("auth/", TelegramLoginVerifyView.as_view(), name="telegram-verify-login"), # Miniapp (POST)
    path("widget-auth/", TelegramWidgetLoginVerifyView.as_view(), name="telegram-widget-login"),  # Widget (GET)
]