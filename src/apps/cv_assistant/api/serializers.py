"""DRF serializers for the cv_assistant app models."""
import nh3
from rest_framework import serializers

from core.markdown import render_markdown

from apps.cv_assistant.models import (
    ChatMessage,
    CVVersion,
    JobApplication,
    RecruiterResponse,
)

# Allow-list for sanitizing rendered chat markdown. Global class attribute
# covers pygments/codehilite hooks; link/image attrs kept for rich replies.
NH3_ATTRIBUTES = {
    "*": {"class"},
    "a": {"href", "title"},
    "img": {"src", "alt"},
    "code": {"class", "data-lang"},
    "span": {"class"},
    "div": {"class", "id"},
    "td": {"class"},
    "th": {"class"},
    "tr": {"class"},
    "table": {"class"},
    "pre": {"class"},
}


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
    """Serializer for the ChatMessage model.

    ``content`` stays the raw (markdown) text; ``content_html`` carries the
    safe server-rendered HTML so chat clients can render rich messages.
    """

    content_html = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "job_application",
            "role",
            "content",
            "content_html",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "job_application"]

    def get_content_html(self, obj):
        """Render markdown to HTML, then sanitize.

        Chat content is LLM output influenced by external job descriptions,
        so raw HTML must never reach the client unescaped. nh3 keeps the
        tags/attributes markdown+pygments legitimately produce.
        """
        html = render_markdown(obj.content)
        return nh3.clean(html, attributes=NH3_ATTRIBUTES)


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