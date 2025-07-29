from rest_framework import serializers
from core.models import Post, PostSchedule

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'

class PostScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostSchedule
        fields = '__all__'