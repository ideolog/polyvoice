from rest_framework import viewsets
from core.models.project import Project
from core.serializers.project import ProjectSerializer

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)