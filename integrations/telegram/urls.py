from django.urls import path
from .views import TelegramSendMessageView, TelegramLoginVerifyView

urlpatterns = [
    path("send/", TelegramSendMessageView.as_view(), name="telegram-send-message"),
    path("auth/", TelegramLoginVerifyView.as_view(), name="telegram-verify-login"),
]