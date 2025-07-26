from rest_framework import serializers
from core.models.project import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'tone', 'frequency', 'created_at']
        read_only_fields = ['id', 'created_at']