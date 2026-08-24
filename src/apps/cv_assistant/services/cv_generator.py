"""Asynchronous CV generation.

POST /jobs/<pk>/generate-cv/ returns 202 immediately; the LLM pipeline runs
in a worker thread and reports progress through ``JobApplication.status``:

    cv_generating -> cv_generated | cv_failed

Rationale: the LLM call legitimately takes up to AI_TIMEOUT (90s), which no
synchronous request can survive across the proxy chain (NGINX Gateway Fabric
default backend timeout is 60s; Cloudflare would cap it at 100s anyway).
Moving generation off the request path makes the endpoint immune to any
proxy/CDN timeout, and the result is durable: a worker restart mid-run is
recovered by the stuck-guard (jobs stuck in cv_generating for more than
STUCK_TIMEOUT are re-claimable).

The chat log gets a system message on completion (success or failure), so
the outcome is always visible in the conversation itself.
"""

import logging
import threading
from datetime import timedelta

from django.conf import settings
from django.db import connection, transaction
from django.db.models import Max
from django.utils import timezone

from apps.cv_assistant.models import CVVersion, ChatMessage, JobApplication
from apps.cv_assistant.services import cv_adapter, cv_builder, pdf_generator
from apps.cv_assistant.services.ai_client import chat_completion

logger = logging.getLogger(__name__)

STATUS_GENERATING = "cv_generating"
STATUS_DONE = "cv_generated"
STATUS_FAILED = "cv_failed"

# A job stuck in cv_generating longer than this is considered dead (e.g. the
# worker was recycled mid-run) and a new generation may claim it again.
STUCK_TIMEOUT = timedelta(minutes=3)


class CVGenerationInProgress(Exception):
    """Raised when a generation is already running for the job application."""


def _build_messages(job_application, user_instructions):
    """Build the [system, user] prompt pair for CV adaptation.

    Includes the job's chat history as context (moved verbatim from the old
    synchronous view).
    """
    conversation_history = list(
        job_application.messages.all().order_by("created_at").values(
            "role", "content"
        )
    )
    base_cv_data = cv_builder.build_cv_context()
    system_prompt = cv_adapter.build_system_prompt(base_cv_data)
    adaptation_prompt = cv_adapter.build_adaptation_prompt(
        job_application.job_description,
        user_instructions,
        conversation_history=conversation_history,
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": adaptation_prompt},
    ]


def run_cv_generation(job_pk, user_instructions=None, prompt_summary=""):
    """Execute the full generation pipeline and update job status.

    Runs in a background thread — must never propagate exceptions: every
    failure path transitions the job to cv_failed and logs a system chat
    message so the user sees what happened.
    """
    try:
        job_application = JobApplication.objects.get(pk=job_pk)
    except JobApplication.DoesNotExist:
        logger.error("cv_generation: job %s disappeared before start", job_pk)
        return

    try:
        _generate(job_application, user_instructions, prompt_summary)
        job_application.status = STATUS_DONE
        job_application.save(update_fields=["status"])
    except Exception as exc:  # noqa: BLE001 — boundary: never crash the thread
        logger.exception("cv_generation: generation failed for job %s", job_pk)
        job_application.status = STATUS_FAILED
        job_application.save(update_fields=["status"])
        job_application.messages.create(
            role=ChatMessage.ROLE_SYSTEM,
            content=f"CV generation failed: {exc}",
        )
    finally:
        # Threads get their own DB connections; close ours so it is not
        # leaked for the lifetime of the worker process. Guarded so inline
        # (main-thread) executions — e.g. tests — keep their connection.
        if threading.current_thread() is not threading.main_thread():
            connection.close()


def _generate(job_application, user_instructions, prompt_summary):
    """LLM call -> parse -> CVVersion -> PDF (raises on any failure)."""
    messages = _build_messages(job_application, user_instructions)

    ai_response = chat_completion(messages)

    try:
        parsed = cv_adapter.parse_ai_response(ai_response)
    except ValueError as exc:
        raise ValueError(f"AI response was not valid: {exc}") from exc

    with transaction.atomic():
        existing_versions = job_application.cv_versions.select_for_update()
        existing_max = existing_versions.aggregate(
            _max_version=Max("version_number"),
        )["_max_version"]
        next_version = (existing_max or 0) + 1

        cv_version = job_application.cv_versions.create(
            version_number=next_version,
            adapted_summary=parsed["summary"],
            adapted_experiences=parsed["experiences"],
            ai_model=settings.AI_MODEL,
            prompt_summary=prompt_summary,
        )

    adapted_data = {
        "summary": parsed["summary"],
        "experiences": parsed["experiences"],
    }
    context = cv_builder.build_cv_context(adapted_data=adapted_data)
    pdf_bytes = pdf_generator.generate_cv_pdf(context)
    pdf_name = f"cv_v{next_version}_{job_application.company}.pdf"
    from django.core.files.base import ContentFile

    cv_version.pdf_file.save(pdf_name, ContentFile(pdf_bytes), save=True)

    job_application.messages.create(
        role=ChatMessage.ROLE_SYSTEM,
        content=f"CV version {next_version} generated successfully.",
    )


def start_cv_generation(job_application, user_instructions=None, prompt_summary=""):
    """Claim the job (status -> cv_generating) and spawn the worker thread.

    Raises CVGenerationInProgress if a live generation is already running.
    A generation older than STUCK_TIMEOUT is treated as dead and re-claimed
    (e.g. after a worker restart mid-run).
    """
    now = timezone.now()
    with transaction.atomic():
        locked = (
            JobApplication.objects.select_for_update()
            .select_related(None)
            .get(pk=job_application.pk)
        )
        if (
            locked.status == STATUS_GENERATING
            and locked.updated_at
            and locked.updated_at > now - STUCK_TIMEOUT
        ):
            raise CVGenerationInProgress(
                "A CV generation is already in progress for this job."
            )
        locked.status = STATUS_GENERATING
        locked.save(update_fields=["status"])

    thread = threading.Thread(
        target=run_cv_generation,
        args=(job_application.pk,),
        kwargs={
            "user_instructions": user_instructions,
            "prompt_summary": prompt_summary,
        },
        name=f"cv-gen-{job_application.pk}",
        daemon=True,
    )
    thread.start()
    return thread
