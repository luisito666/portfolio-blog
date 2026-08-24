"""DRF views for the cv_assistant app."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Max

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cv_assistant.models import (
    ChatMessage,
    CVVersion,
    JobApplication,
    RecruiterResponse,
)
from apps.cv_assistant.services import cv_adapter, cv_builder, pdf_generator
from apps.cv_assistant.services.ai_client import chat_completion
from apps.cv_assistant.services.cv_generator import (
    CVGenerationInProgress,
    start_cv_generation,
)

from .permissions import IsAdminUser
from .serializers import (
    ChatMessageSerializer,
    CVVersionSerializer,
    JobApplicationSerializer,
    RecruiterResponseSerializer,
)


class JobApplicationViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for JobApplication records (staff only)."""

    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAdminUser]

    # ------------------------------------------------------------------
    # Task 9: Chat endpoints — list and send messages.
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get", "post"], url_path="messages")
    def messages(self, request, pk=None):
        """GET: list messages for this job application.

        POST: save the user message, call the AI, save the AI reply and return
        both the user and assistant messages. Requires {"content": "..."} in the
        request body.
        """
        job_application = self.get_object()
        messages_qs = job_application.messages.all().order_by("created_at")

        if request.method == "GET":
            serializer = ChatMessageSerializer(messages_qs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # POST — send a user message and get the AI reply
        content = request.data.get("content")
        if not content:
            return Response(
                {"detail": "'content' is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Persist the user message.
        user_message = job_application.messages.create(
            role=ChatMessage.ROLE_USER,
            content=content,
        )

        # 2. Build the conversation context for the AI.
        # The system prompt carries the CV + job description as read-only
        # context. It explicitly forbids dumping a full adapted CV in the
        # chat — that is the "Generate CV" button's job.
        base_cv_data = cv_builder.build_cv_context()
        system_prompt = cv_adapter.build_chat_system_prompt(
            base_cv_data,
            job_description=job_application.job_description,
        )
        conversation = [{"role": "system", "content": system_prompt}]

        # Add prior messages from DB (excluding the just-created user message)
        prior = messages_qs.exclude(pk=user_message.pk).values("role", "content")
        for m in prior:
            conversation.append({"role": m["role"], "content": m["content"]})

        # ALWAYS add the new user message (never discard it)
        conversation.append({"role": "user", "content": user_message.content})

        # 3. Call the AI client.
        try:
            ai_response = chat_completion(conversation)
        except Exception:
            return Response(
                {"detail": "AI service temporarily unavailable. Please try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # 4. Persist the assistant reply.
        assistant_message = job_application.messages.create(
            role=ChatMessage.ROLE_ASSISTANT,
            content=ai_response,
        )

        serializer = ChatMessageSerializer(
            [user_message, assistant_message], many=True
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # Task 10: Generate an adapted CV version for this job application.
    # ------------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="generate-cv")
    def generate_cv(self, request, pk=None):
        """Asynchronously generate an AI-adapted CV version for this job.

        Returns 202 immediately; the LLM pipeline runs in a background
        thread and reports progress through the job's ``status`` field:
        ``cv_generating`` -> ``cv_generated`` | ``cv_failed``. Poll
        ``GET /jobs/<pk>/`` for status; the new CVVersion (with PDF) appears
        in ``GET /cv-versions/?job=<pk>`` on success.

        The async design exists because the LLM call legitimately takes up
        to AI_TIMEOUT (90s) and no synchronous request survives the proxy
        chain (NGINX Gateway Fabric backend timeout 60s, Cloudflare 100s).
        """
        job_application = self.get_object()

        try:
            start_cv_generation(
                job_application,
                user_instructions=request.data.get("user_instructions"),
                prompt_summary=request.data.get("prompt_summary", ""),
            )
        except CVGenerationInProgress:
            return Response(
                {"detail": "CV generation already in progress."},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": "CV generation started."},
            status=status.HTTP_202_ACCEPTED,
        )

    # ------------------------------------------------------------------
    # Task 13: Dashboard endpoint — CV success metrics.
    # ------------------------------------------------------------------
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request, pk=None):
        """Return aggregate CV success metrics for the dashboard."""
        from django.db.models import Count

        # Totals
        total_applications = JobApplication.objects.count()
        total_cv_versions = CVVersion.objects.count()

        # Status breakdown: {status_value: count}
        status_breakdown = {}
        status_counts = (
            JobApplication.objects.values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
        for entry in status_counts:
            status_breakdown[entry["status"]] = entry["count"]

        # Response breakdown: {response_type: count}
        response_breakdown = {}
        response_counts = (
            RecruiterResponse.objects.values("response_type")
            .annotate(count=Count("id"))
            .order_by("response_type")
        )
        for entry in response_counts:
            response_breakdown[entry["response_type"]] = entry["count"]

        # Recent applications (5 most recent)
        recent_qs = JobApplication.objects.order_by("-created_at")[:5]
        recent_serializer = JobApplicationSerializer(recent_qs, many=True)

        return Response(
            {
                "total_applications": total_applications,
                "total_cv_versions": total_cv_versions,
                "status_breakdown": status_breakdown,
                "response_breakdown": response_breakdown,
                "recent_applications": recent_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class CVVersionViewSet(viewsets.ModelViewSet):
    """CRUD + regenerate endpoints for CVVersion records (staff only)."""

    queryset = CVVersion.objects.all()
    serializer_class = CVVersionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        job_id = self.request.query_params.get("job")
        if job_id:
            queryset = queryset.filter(job_application_id=job_id)
        return queryset

    # ------------------------------------------------------------------
    # Task 11: Regenerate the PDF from the saved adapted data.
    # ------------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="regenerate-pdf")
    def regenerate_pdf(self, request, pk=None):
        """Re-render the PDF for this CV version from its stored adapted data.

        Useful when the PDF template changes or the original file was lost.
        Overwrites the existing ``pdf_file``.
        """
        cv_version = self.get_object()

        # 1. Rebuild the adapted context from the stored fields.
        adapted_data = {
            "summary": cv_version.adapted_summary or "",
            "experiences": cv_version.adapted_experiences or [],
        }
        context = cv_builder.build_cv_context(adapted_data=adapted_data)

        # 2. Generate the PDF bytes.
        pdf_bytes = pdf_generator.generate_cv_pdf(context)

        # 3. Overwrite the existing file (or create a new one).
        existing_name = cv_version.pdf_file.name if cv_version.pdf_file else None
        pdf_name = (
            existing_name.split("/")[-1] if existing_name
            else f"cv_v{cv_version.version_number}_regenerated.pdf"
        )
        cv_version.pdf_file.save(pdf_name, ContentFile(pdf_bytes), save=True)

        # 4. Return the updated CV version.
        serializer = CVVersionSerializer(cv_version)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecruiterResponseViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for RecruiterResponse records (staff only)."""

    queryset = RecruiterResponse.objects.all()
    serializer_class = RecruiterResponseSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        job_id = self.request.query_params.get("job")
        if job_id:
            queryset = queryset.filter(cv_version__job_application_id=job_id)
        return queryset

    # ------------------------------------------------------------------
    # Task 12: Update parent JobApplication status on response creation.
    # ------------------------------------------------------------------
    def perform_create(self, serializer):
        """Save the recruiter response, then mark the parent job application
        as 'responded'.
        """
        recruiter_response = serializer.save()
        job_application = recruiter_response.cv_version.job_application
        job_application.status = "responded"
        job_application.save()