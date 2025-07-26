from rest_framework import serializers
from core.models.channel import Channel

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ['id', 'project', 'name',  'external_id', 'type', 'credentials', 'created_at']
        read_only_fields = ['id', 'created_at']