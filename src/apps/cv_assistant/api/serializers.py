"""DRF serializers for the cv_assistant app models."""
from rest_framework import serializers

from apps.cv_assistant.models import (
    ChatMessage,
    CVVersion,
    JobApplication,
    RecruiterResponse,
)


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for the JobApplication model."""

    class Meta:
        model = JobApplication
        fields = [
            "id",
            "company",
            "position",
            "job_description",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for the ChatMessage model."""

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "job_application",
            "role",
            "content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "job_application"]


class CVVersionSerializer(serializers.ModelSerializer):
    """Serializer for the CVVersion model."""

    class Meta:
        model = CVVersion
        fields = [
            "id",
            "job_application",
            "version_number",
            "adapted_summary",
            "adapted_experiences",
            "adapted_certifications",
            "adapted_education",
            "ai_model",
            "prompt_summary",
            "pdf_file",
            "created_at",
            "is_final",
        ]
        read_only_fields = ["id", "version_number", "created_at", "ai_model"]


class RecruiterResponseSerializer(serializers.ModelSerializer):
    """Serializer for the RecruiterResponse model."""

    class Meta:
        model = RecruiterResponse
        fields = [
            "id",
            "cv_version",
            "response_type",
            "notes",
            "responded_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]