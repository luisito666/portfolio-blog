"""DRF views for the cv_assistant app."""
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Max

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cv_assistant.models import ChatMessage, CVVersion, JobApplication
from apps.cv_assistant.services import cv_adapter, cv_builder, pdf_generator
from apps.cv_assistant.services.ai_client import chat_completion

from .permissions import IsAdminUser
from .serializers import (
    ChatMessageSerializer,
    CVVersionSerializer,
    JobApplicationSerializer,
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
        prior = messages_qs.exclude(pk=user_message.pk).values("role", "content")
        conversation = [{"role": m["role"], "content": m["content"]} for m in prior]

        is_first = len(conversation) == 0
        if is_first:
            base_cv_data = cv_builder.build_cv_context()
            system_prompt = cv_adapter.build_system_prompt(base_cv_data)
            adaptation_prompt = cv_adapter.build_adaptation_prompt(
                job_application.job_description
            )
            conversation = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": adaptation_prompt},
            ]

        # Append the new user message, UNLESS it is the first message (in which
        # case the adaptation prompt already represents it).
        if not is_first:
            conversation.append(
                {"role": ChatMessage.ROLE_USER, "content": user_message.content}
            )

        # 3. Call the AI client.
        ai_response = chat_completion(conversation)

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
        """Generate an AI-adapted CV version (with PDF) for this job application.

        Accepts optional ``user_instructions`` and ``prompt_summary`` in the
        request body. Creates a new ``CVVersion`` with an incrementing
        ``version_number``, generates the PDF, and marks the job application
        status as ``'cv_generated'``.
        """
        job_application = self.get_object()

        # 1-2. Build the base CV context and prompt messages.
        base_cv_data = cv_builder.build_cv_context()
        system_prompt = cv_adapter.build_system_prompt(base_cv_data)
        adaptation_prompt = cv_adapter.build_adaptation_prompt(
            job_application.job_description,
            request.data.get("user_instructions"),
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": adaptation_prompt},
        ]

        # 3. Call the AI and parse the structured response.
        ai_response = chat_completion(messages)
        parsed = cv_adapter.parse_ai_response(ai_response)

        # 4. Determine the next version_number.
        existing_max = job_application.cv_versions.aggregate(
            _max_version=Max("version_number"),
        )["_max_version"]
        next_version = (existing_max or 0) + 1

        # 5. Create the CVVersion record.
        cv_version = job_application.cv_versions.create(
            version_number=next_version,
            adapted_summary=parsed["summary"],
            adapted_experiences=parsed["experiences"],
            ai_model=settings.AI_MODEL,
            prompt_summary=request.data.get("prompt_summary", ""),
        )

        # 6. Build the adapted context and generate the PDF.
        adapted_data = {
            "summary": parsed["summary"],
            "experiences": parsed["experiences"],
        }
        context = cv_builder.build_cv_context(adapted_data=adapted_data)
        pdf_bytes = pdf_generator.generate_cv_pdf(context)
        pdf_name = f"cv_v{next_version}_{job_application.company}.pdf"
        cv_version.pdf_file.save(pdf_name, ContentFile(pdf_bytes), save=True)

        # 7. Update the job application status.
        job_application.status = "cv_generated"
        job_application.save()

        # 8. Return the serialized CV version.
        serializer = CVVersionSerializer(cv_version)
        return Response(serializer.data, status=status.HTTP_201_CREATED)