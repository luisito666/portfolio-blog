from django.contrib import admin
from .models import About, Skill, Project, SocialSettings, Experience, Summary, Certification, Education, Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['name', 'email']
    readonly_fields = ['downloaded_at']

@admin.register(SocialSettings)
class SocialSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'linkedin_url', 'twitter_url', 'facebook_url', 'github_url']
    
    def has_add_permission(self, request):
        # Check if an instance already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'profile_image')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Check if an instance already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'years_of_experience', 'created_at']
    list_filter = ['category', 'years_of_experience']
    search_fields = ['name', 'category']
    list_editable = ['years_of_experience']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'featured', 'created_at', 'updated_at']
    list_filter = ['featured', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'technologies']
    list_editable = ['featured']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Project Information', {
            'fields': ('title', 'description', 'image', 'technologies')
        }),
        ('Links', {
            'fields': ('github_url', 'live_url'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('featured',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'start_date', 'end_date', 'current', 'created_at']
    list_filter = ['current', 'start_date', 'created_at']
    search_fields = ['company', 'position', 'description', 'location']
    list_editable = ['current']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Experience Information', {
            'fields': ('company', 'position', 'location', 'company_url')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Employment Period', {
            'fields': ('start_date', 'end_date', 'current')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Check if an instance already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['name', 'issuing_organization', 'issue_date', 'expiry_date', 'is_expired']
    list_filter = ['issue_date', 'issuing_organization']
    search_fields = ['name', 'issuing_organization', 'credential_id']
    readonly_fields = ['created_at', 'updated_at', 'is_expired']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Certification Information', {
            'fields': ('name', 'issuing_organization', 'description')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Credential Details', {
            'fields': ('credential_id', 'credential_url'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'is_expired'),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'field_of_study', 'institution', 'start_date', 'end_date', 'current']
    list_filter = ['current', 'start_date', 'institution']
    search_fields = ['institution', 'degree', 'field_of_study', 'description']
    list_editable = ['current']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Education Information', {
            'fields': ('institution', 'degree', 'field_of_study', 'location', 'institution_url')
        }),
        ('Academic Details', {
            'fields': ('grade', 'description')
        }),
        ('Study Period', {
            'fields': ('start_date', 'end_date', 'current')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
