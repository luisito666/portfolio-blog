"""DRF views for the blog app."""
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from apps.blog.models import BlogPost
from .serializers import BlogPostSerializer


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Authenticated users may write. Reads of published posts are public."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)


class BlogPostViewSet(viewsets.ModelViewSet):
    """ViewSet for BlogPost with auth-protected writes.

    - list / retrieve: public for published posts
    - create / update / partial_update / destroy: requires JWT auth
    """

    queryset = BlogPost.objects.all().order_by('-published_at', '-created_at')
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthorOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        if not (self.request.user and self.request.user.is_authenticated):
            qs = qs.filter(published=True)
        return qs

    def perform_destroy(self, instance):
        if not (self.request.user and self.request.user.is_authenticated):
            raise PermissionDenied("Authentication required to delete posts.")
        instance.delete()

    @action(detail=False, methods=['get'], url_path='published')
    def published(self, request):
        """List only published posts (public endpoint)."""
        qs = BlogPost.objects.filter(published=True).order_by('-published_at', '-created_at')
        page = self.paginate_queryset(qs)
        serializer = BlogPostSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
