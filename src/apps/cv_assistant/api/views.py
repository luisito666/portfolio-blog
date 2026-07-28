"""DRF views for the cv_assistant app."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.cv_assistant.models import ChatMessage, JobApplication
from apps.cv_assistant.services import cv_builder, cv_adapter
from apps.cv_assistant.services.ai_client import chat_completion

from .permissions import IsAdminUser
from .serializers import ChatMessageSerializer, JobApplicationSerializer


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