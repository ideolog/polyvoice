from rest_framework import viewsets
from core.models.channel import Channel
from core.serializers.channel import ChannelSerializer

class ChannelViewSet(viewsets.ModelViewSet):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer