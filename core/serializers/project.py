# core/serializers/project.py

from rest_framework import serializers
from core.models.project import Project
from core.models.project_membership import ProjectMembership

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "created_at"]

    def validate_name(self, value):
        user = self.context["request"].user
        # Check if user already has a project with this name
        if Project.objects.filter(memberships__user=user, name=value).exists():
            raise serializers.ValidationError("You already have a project with this name.")
        return value
