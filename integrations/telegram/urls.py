from django.urls import path
from .views import TelegramSendMessageView

urlpatterns = [
    path("send/", TelegramSendMessageView.as_view(), name="telegram-send-message"),
]