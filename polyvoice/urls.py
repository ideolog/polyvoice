from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import ProjectViewSet, ChannelViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'channels', ChannelViewSet, basename='channel')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]