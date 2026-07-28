"""DRF views for the cv_assistant app."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cv_assistant.models import JobApplication

from .permissions import IsAdminUser
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for JobApplication records (staff only)."""

    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAdminUser]