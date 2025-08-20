# core/serializers/project_membership.py

from rest_framework import serializers
from core.models.project_membership import ProjectMembership

class ProjectMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = ProjectMembership
        fields = ["id", "user", "user_email", "project", "project_name", "role", "joined_at"]
        read_only_fields = ["joined_at"]
