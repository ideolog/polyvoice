from rest_framework import serializers
from core.models.project import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "tone", "frequency", "created_at"]

    def validate_name(self, value):
        user = self.context["request"].user
        if Project.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("You already have a project with this name.")
        return value
