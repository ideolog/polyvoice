# core/views/project.py

from rest_framework import viewsets, permissions
from core.models.project import Project
from core.models.project_membership import ProjectMembership
from core.serializers.project import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # показываем только проекты, где юзер состоит
        return Project.objects.filter(memberships__user=self.request.user).distinct()

    def perform_create(self, serializer):
        project = serializer.save()
        # автоматически создаём membership для владельца
        ProjectMembership.objects.create(
            project=project,
            user=self.request.user,
            role="owner"
        )
