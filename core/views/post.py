from rest_framework import viewsets
from core.models import Post, PostSchedule
from core.serializers.post import PostSerializer, PostScheduleSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

class PostScheduleViewSet(viewsets.ModelViewSet):
    queryset = PostSchedule.objects.all().order_by('-published_at')
    serializer_class = PostScheduleSerializer