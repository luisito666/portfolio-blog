"""DRF serializers for the blog app."""
from rest_framework import serializers
from apps.blog.models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    """Full serializer for BlogPost — used for create/update/retrieve."""

    class Meta:
        model = BlogPost
        fields = [
            'id',
            'title',
            'slug',
            'content',
            'excerpt',
            'featured_image',
            'published',
            'created_at',
            'updated_at',
            'published_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at', 'published_at']

    def validate_title(self, value: str) -> str:
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title must be 200 characters or fewer.")
        return value

    def validate_content(self, value: str) -> str:
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError("Content cannot be empty.")
        return value
