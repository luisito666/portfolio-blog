from django.db import models


class JobApplication(models.Model):
    """A job the user is applying to and wants to tailor a CV for."""

    STATUS_DRAFT = 'draft'
    # Status is a free-form short string; 'draft' is the default. Additional
    # common values include 'in_progress', 'sent', 'closed', etc.

    company = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    job_description = models.TextField()
    status = models.CharField(max_length=20, default=STATUS_DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"

    def __str__(self):
        return f"{self.position} at {self.company}"


class ChatMessage(models.Model):
    """A single message in the conversation about a job application."""

    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_SYSTEM = 'system'

    job_application = models.ForeignKey(
        JobApplication,
        related_name='messages',
        on_delete=models.CASCADE,
    )
    role = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class CVVersion(models.Model):
    """An adapted version of the CV produced for a specific job application."""

    job_application = models.ForeignKey(
        JobApplication,
        related_name='cv_versions',
        on_delete=models.CASCADE,
    )
    version_number = models.PositiveIntegerField()
    adapted_summary = models.TextField(blank=True, null=True)
    # List of {"id": <experience_id>, "position": str, "company": str,
    #          "description_adapted": str}
    adapted_experiences = models.JSONField(default=list)
    adapted_certifications = models.JSONField(default=list)
    adapted_education = models.JSONField(default=list)
    ai_model = models.CharField(max_length=100, blank=True)
    prompt_summary = models.TextField(
        blank=True,
        help_text="Brief note of what was adapted",
    )
    pdf_file = models.FileField(upload_to='cv_versions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_final = models.BooleanField(
        default=False,
        help_text="Marked when sent to company",
    )

    class Meta:
        ordering = ['-version_number']
        verbose_name = "CV Version"
        verbose_name_plural = "CV Versions"

    def __str__(self):
        return f"CV v{self.version_number} for {self.job_application}"


class RecruiterResponse(models.Model):
    """Feedback received from a recruiter/company about a CV version."""

    cv_version = models.ForeignKey(
        CVVersion,
        related_name='responses',
        on_delete=models.CASCADE,
    )
    response_type = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)
    responded_at = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recruiter Response"
        verbose_name_plural = "Recruiter Responses"

    def __str__(self):
        return f"{self.response_type} for {self.cv_version}"