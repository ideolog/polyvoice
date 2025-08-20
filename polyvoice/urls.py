# polyvoice/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import ProjectViewSet, ChannelViewSet, PostViewSet, PostScheduleViewSet
from users.views import MeView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'posts', PostViewSet)
router.register(r'post-schedules', PostScheduleViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("api/telegram/", include("integrations.telegram.urls")),
    path("api/me/", MeView.as_view()),  # ← новый
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)