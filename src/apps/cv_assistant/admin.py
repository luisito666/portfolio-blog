from django.contrib import admin
from .models import JobApplication, ChatMessage, CVVersion, RecruiterResponse


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['company', 'position', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['company', 'position']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['job_application', 'role', 'created_at']
    list_filter = ['role']
    readonly_fields = ['created_at']


@admin.register(CVVersion)
class CVVersionAdmin(admin.ModelAdmin):
    list_display = [
        'job_application',
        'version_number',
        'ai_model',
        'is_final',
        'created_at',
    ]
    list_filter = ['is_final']
    readonly_fields = ['created_at', 'version_number', 'ai_model']
    search_fields = ['job_application__company']


@admin.register(RecruiterResponse)
class RecruiterResponseAdmin(admin.ModelAdmin):
    list_display = ['cv_version', 'response_type', 'responded_at', 'created_at']
    list_filter = ['response_type']
    readonly_fields = ['created_at']