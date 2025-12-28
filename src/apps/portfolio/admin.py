from django.contrib import admin
from .models import About, Skill, Project, SocialSettings, Experience

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
