from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import ProjectViewSet, ChannelViewSet, PostViewSet, PostScheduleViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'channels', ChannelViewSet, basename='channel')
router.register(r'posts', PostViewSet)
router.register(r'post-schedules', PostScheduleViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path("api/telegram/", include("integrations.telegram.urls")),
]